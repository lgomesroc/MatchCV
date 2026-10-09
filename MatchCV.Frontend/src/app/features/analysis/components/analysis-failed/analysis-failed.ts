
import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-analysis-failed',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './analysis-failed.html',
  styleUrl: './analysis-failed.scss',
})
export class AnalysisFailedComponent {
  @Input() errorMessage = '';

  @Output() back = new EventEmitter<void>();

  onBack(): void {
    this.back.emit();
  }
}
