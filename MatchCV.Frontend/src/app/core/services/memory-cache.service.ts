import { Injectable } from '@angular/core';
import {
  Observable,
  defer,
  finalize,
  shareReplay,
  tap,
} from 'rxjs';

interface CacheEntry<T> {
  value: T;
  expiresAt: number;
}

@Injectable({
  providedIn: 'root',
})
export class MemoryCacheService {
  private readonly entries = new Map<string, CacheEntry<unknown>>();
  private readonly inFlight = new Map<string, Observable<unknown>>();

  get<T>(key: string): T | undefined {
    const entry = this.entries.get(key);

    if (!entry) {
      return undefined;
    }

    if (Date.now() >= entry.expiresAt) {
      this.entries.delete(key);
      return undefined;
    }

    return entry.value as T;
  }

  has(key: string): boolean {
    return this.get(key) !== undefined;
  }

  set<T>(
    key: string,
    value: T,
    ttlMs: number,
  ): void {
    if (!key.trim()) {
      throw new Error('A chave do cache é obrigatória.');
    }

    if (!Number.isFinite(ttlMs) || ttlMs <= 0) {
      throw new Error('O TTL deve ser maior que zero.');
    }

    this.entries.set(key, {
      value,
      expiresAt: Date.now() + ttlMs,
    });
  }

  getOrLoad<T>(
    key: string,
    loader: () => Observable<T>,
    ttlMs: number,
  ): Observable<T> {
    return defer(() => {
      const cached = this.get<T>(key);

      if (cached !== undefined) {
        return new Observable<T>((subscriber) => {
          subscriber.next(cached);
          subscriber.complete();
        });
      }

      const existingRequest = this.inFlight.get(key);

      if (existingRequest) {
        return existingRequest as Observable<T>;
      }

      let sharedRequest: Observable<T>;

      sharedRequest = defer(loader).pipe(
        tap((value) => {
          this.set(key, value, ttlMs);
        }),
        finalize(() => {
          if (this.inFlight.get(key) === sharedRequest) {
            this.inFlight.delete(key);
          }
        }),
        shareReplay({
          bufferSize: 1,
          refCount: false,
        }),
      );

      this.inFlight.set(key, sharedRequest);

      return sharedRequest;
    });
  }

  invalidate(key: string): void {
    this.entries.delete(key);
    this.inFlight.delete(key);
  }

  invalidatePrefix(prefix: string): void {
    for (const key of this.entries.keys()) {
      if (key.startsWith(prefix)) {
        this.entries.delete(key);
      }
    }

    for (const key of this.inFlight.keys()) {
      if (key.startsWith(prefix)) {
        this.inFlight.delete(key);
      }
    }
  }

  clear(): void {
    this.entries.clear();
    this.inFlight.clear();
  }

  get size(): number {
    return this.entries.size;
  }
}
