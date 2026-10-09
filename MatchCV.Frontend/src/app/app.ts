import { Component } from '@angular/core';
import { AnalysisComponent } from './features/analysis/analysis';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    AnalysisComponent,
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  title = 'MatchCV';
}
