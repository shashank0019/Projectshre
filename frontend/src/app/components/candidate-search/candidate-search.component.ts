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
            <strong>Skills <span class="model-badge">all-MiniLM-L6-v2</span></strong>
            <div class="skills-list">
              <div *ngFor="let skill of candidate.skills" class="skill-row">
                <div class="skill-header-row">
                  <span class="skill-name">{{ skill }}</span>
                  <span class="skill-pct" [class.high]="getSkillPct(candidate, skill) >= 60"
                                          [class.mid]="getSkillPct(candidate, skill) >= 30 && getSkillPct(candidate, skill) < 60"
                                          [class.low]="getSkillPct(candidate, skill) < 30">
                    {{ getSkillPct(candidate, skill) }}%
                  </span>
                </div>
                <div class="skill-bar-bg">
                  <div class="skill-bar-fill"
                       [style.width.%]="getSkillPct(candidate, skill)"
                       [class.high]="getSkillPct(candidate, skill) >= 60"
                       [class.mid]="getSkillPct(candidate, skill) >= 30 && getSkillPct(candidate, skill) < 60"
                       [class.low]="getSkillPct(candidate, skill) < 30">
                  </div>
                </div>
              </div>
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
      padding-top: 12px;
    }

    .model-badge {
      font-size: 10px;
      font-weight: 500;
      background: #e8f0fe;
      color: #3c55a5;
      padding: 2px 7px;
      border-radius: 10px;
      margin-left: 6px;
      vertical-align: middle;
      letter-spacing: 0.2px;
    }

    .skills-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 12px;
    }

    .skill-row {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .skill-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .skill-name {
      font-size: 13px;
      font-weight: 500;
      color: #2c3e50;
    }

    .skill-pct {
      font-size: 12px;
      font-weight: 700;
      min-width: 38px;
      text-align: right;
    }
    .skill-pct.high { color: #1e8e3e; }
    .skill-pct.mid  { color: #c97700; }
    .skill-pct.low  { color: #1565c0; }

    .skill-bar-bg {
      width: 100%;
      height: 6px;
      background: #e0e0e0;
      border-radius: 4px;
      overflow: hidden;
    }

    .skill-bar-fill {
      height: 100%;
      border-radius: 4px;
      transition: width 0.5s ease;
    }
    .skill-bar-fill.high { background: linear-gradient(90deg, #34a853, #1e8e3e); }
    .skill-bar-fill.mid  { background: linear-gradient(90deg, #fbbc04, #c97700); }
    .skill-bar-fill.low  { background: linear-gradient(90deg, #4285f4, #1565c0); }
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

  /** Return the per-skill relevance % from all-MiniLM-L6-v2, or 0 if not available */
  getSkillPct(candidate: any, skill: string): number {
    if (candidate.skill_scores && candidate.skill_scores[skill] !== undefined) {
      return candidate.skill_scores[skill];
    }
    return 0;
  }
}
