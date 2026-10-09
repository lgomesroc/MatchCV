
import { CommonModule } from '@angular/common';
import {
  Component,
  ElementRef,
  EventEmitter,
  Input,
  Output,
  ViewChild,
} from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-analysis-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './analysis-input.html',
  styleUrl: './analysis-input.scss',
})
export class AnalysisInputComponent {
  @Input() jobDescription = '';
  @Input() resumeText = '';
  @Input() selectedFile: File | null = null;
  @Input() errorMessage = '';
  @Input() canAnalyze = false;

  @Output() jobDescriptionChange = new EventEmitter<string>();
  @Output() resumeTextChange = new EventEmitter<string>();
  @Output() fileSelected = new EventEmitter<Event>();
  @Output() clearFile = new EventEmitter<void>();
  @Output() clearText = new EventEmitter<void>();
  @Output() analyze = new EventEmitter<void>();

  @ViewChild('resumeFileInput')
  private resumeFileInput?: ElementRef<HTMLInputElement>;

  readonly maxJobDescriptionCharacters = 3000;

  onJobDescriptionChange(value: string): void {
    this.jobDescriptionChange.emit(value);
  }

  onResumeTextChange(value: string): void {
    this.resumeTextChange.emit(value);
  }

  onFileSelected(event: Event): void {
    this.fileSelected.emit(event);
  }

  onClearFile(): void {
    this.clearFile.emit();

    if (this.resumeFileInput) {
      this.resumeFileInput.nativeElement.value = '';
    }
  }

  onClearText(): void {
    this.clearText.emit();
  }

  onAnalyze(): void {
    this.analyze.emit();
  }
}
