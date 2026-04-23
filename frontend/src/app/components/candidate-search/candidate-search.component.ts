import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CandidateService } from '../../services/candidate.service';
import { SearchResponse } from '../../models/candidate.model';

@Component({
  selector: 'app-candidate-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="search-container">
      <h2>🔍 Search Candidates</h2>
      
      <div class="search-box">
        <input 
          type="text" 
          [(ngModel)]="searchQuery" 
          placeholder="e.g., Python developer with 2 years experience"
          (keyup.enter)="performSearch()"
        />
        <button (click)="performSearch()" [disabled]="isLoading">
          {{ isLoading ? 'Searching...' : 'Search' }}
        </button>
      </div>

      <div *ngIf="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div *ngIf="searchResults" class="results-container">
        <h3>Results ({{ searchResults.total }} found)</h3>
        
        <div *ngIf="searchResults.candidates.length === 0" class="no-results">
          No candidates found. Try uploading resumes first.
        </div>

        <div *ngFor="let candidate of searchResults.candidates" class="candidate-card">
          <div class="candidate-header">
            <h4>{{ candidate.name }}</h4>
            <span class="rank">Rank #{{ candidate.rank }}</span>
          </div>
          
          <div class="candidate-body">
            <div class="score-display">
              <div class="score-circle">{{ (candidate.score * 100).toFixed(1) }}%</div>
            </div>
            
            <div class="candidate-details">
              <p><strong>Experience:</strong> {{ candidate.experience }}</p>
              <p><strong>MCQ Score:</strong> {{ candidate.mcqScore || 'N/A' }}</p>
            </div>
          </div>

          <div class="skills-section">
            <strong>Skills:</strong>
            <div class="skills-list">
              <span *ngFor="let skill of candidate.skills" class="skill-tag">
                {{ skill }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .search-container {
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    h2 {
      margin-bottom: 20px;
      color: #2c3e50;
    }

    .search-box {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }

    .search-box input {
      flex: 1;
      padding: 12px;
      border: 2px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
    }

    .search-box input:focus {
      border-color: #007bff;
      box-shadow: 0 0 5px rgba(0, 123, 255, 0.3);
    }

    .search-box button {
      padding: 12px 30px;
    }

    .error-message {
      background-color: #f8d7da;
      color: #721c24;
      padding: 12px;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .results-container {
      margin-top: 30px;
    }

    .results-container h3 {
      margin-bottom: 20px;
      color: #2c3e50;
    }

    .no-results {
      text-align: center;
      padding: 40px;
      color: #999;
      background: #f9f9f9;
      border-radius: 4px;
    }

    .candidate-card {
      background: #f9f9f9;
      padding: 20px;
      margin-bottom: 15px;
      border-radius: 6px;
      border-left: 4px solid #007bff;
    }

    .candidate-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
    }

    .candidate-header h4 {
      margin: 0;
      color: #2c3e50;
    }

    .rank {
      background: #007bff;
      color: white;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: bold;
    }

    .candidate-body {
      display: flex;
      gap: 20px;
      margin-bottom: 15px;
    }

    .score-display {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .score-circle {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: linear-gradient(135deg, #007bff, #0056b3);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      font-weight: bold;
    }

    .candidate-details {
      flex: 1;
    }

    .candidate-details p {
      margin: 8px 0;
      font-size: 14px;
    }

    .skills-section {
      border-top: 1px solid #ddd;
      padding-top: 10px;
    }

    .skills-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }

    .skill-tag {
      background: #e3f2fd;
      color: #1976d2;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
    }
  `]
})
export class CandidateSearchComponent implements OnInit {
  searchQuery: string = '';
  searchResults: SearchResponse | null = null;
  isLoading: boolean = false;
  errorMessage: string = '';

  constructor(private candidateService: CandidateService) {}

  ngOnInit(): void {
    // Initialize component
  }

  performSearch(): void {
    if (!this.searchQuery.trim()) {
      this.errorMessage = 'Please enter a search query';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.candidateService.searchCandidates({ query: this.searchQuery }).subscribe({
      next: (response) => {
        this.searchResults = response;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = error.error?.message || 'Error searching candidates. Please try again.';
        this.isLoading = false;
      }
    });
  }
}
