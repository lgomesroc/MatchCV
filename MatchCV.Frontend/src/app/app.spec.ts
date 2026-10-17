
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { App } from './app';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([])],
    }).compileComponents();
  });

  it('deve criar o componente principal', () => {
    const fixture = TestBed.createComponent(App);

    expect(fixture.componentInstance).toBeTruthy();
  });

  it('deve renderizar o elemento raiz', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    expect(fixture.nativeElement).toBeTruthy();
  });
});
