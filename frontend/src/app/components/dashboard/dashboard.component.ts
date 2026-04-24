import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CandidateService } from '../../services/candidate.service';
import { Candidate } from '../../models/candidate.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="dashboard-container">
      <div class="header">
        <h2>📊 Dashboard</h2>
      </div>

      <div class="search-section" *ngIf="candidates.length > 0">
        <h3>🔍 Search Candidates</h3>
        <div class="search-controls">
          <div class="search-input-group">
            <label>Skills (comma-separated):</label>
            <input 
              type="text" 
              [(ngModel)]="searchSkills" 
              placeholder="e.g., Python, Java, React"
              class="search-input"
            />
          </div>
          <div class="search-input-group">
            <label>Years of Experience:</label>
            <input 
              type="number" 
              [(ngModel)]="searchExperience" 
              placeholder="e.g., 5"
              class="search-input"
              min="0"
            />
          </div>
          <button (click)="performSearch()" class="btn-search">
            Search
          </button>
          <button (click)="clearSearch()" class="btn-clear-search">
            Clear Results
          </button>
        </div>
      </div>

      <div class="search-results" *ngIf="searchResults.length > 0">
        <h3>🏆 Search Results (Ranked)</h3>
        <div class="candidates-list">
          <div *ngFor="let candidate of searchResults" class="candidate-item result-item">
            <div class="result-rank">
              <span class="rank-badge">{{ candidate.rank }}</span>
            </div>
            <div class="result-info">
              <div class="result-header-row">
                <div class="candidate-name">{{ candidate.name }}</div>
                <div class="result-score" *ngIf="candidate.percentage">
                  ✓ <strong>{{ candidate.percentage }}%</strong> overall
                </div>
              </div>
              <div class="result-meta" *ngIf="candidate.experience">
                📅 {{ candidate.experience }} yrs experience
              </div>

              <!-- Only show skills the user searched for -->
              <div class="resume-skills" *ngIf="getMatchedSkills(candidate).length > 0">
                <div class="skills-label">Matched Skills <span class="model-tag">all-MiniLM-L6-v2</span></div>
                <div class="skill-bars">
                  <div *ngFor="let skill of getMatchedSkills(candidate)" class="skill-row">
                    <div class="skill-meta">
                      <span class="skill-name">{{ skill }}</span>
                      <span class="skill-pct"
                            [class.high]="getSkillPct(candidate, skill) >= 60"
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
      </div>

      <div class="upload-section">
        <h3>📤 Upload Resumes</h3>
        <div class="upload-area" (click)="fileInput.click()">
          <p>Click to upload or drag and drop</p>
          <p class="file-info">PDF or DOCX (Multiple files allowed)</p>
          <input 
            type="file" 
            #fileInput 
            hidden 
            multiple 
            accept=".pdf,.docx"
            (change)="onFileSelected($event)"
          />
        </div>
        
        <div *ngIf="uploadMessage" [ngClass]="{'success': uploadSuccess, 'error': !uploadSuccess}" class="message">
          {{ uploadMessage }}
        </div>

        <div *ngIf="isUploading" class="progress">
          <div class="progress-bar">Uploading...</div>
        </div>

        <button 
          *ngIf="candidates.length > 0" 
          (click)="clearCandidates()" 
          class="btn-delete"
        >
          Clear All Candidates
        </button>
      </div>

      <div class="stats-section" *ngIf="candidates.length > 0">
        <h3>📈 Statistics</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ candidates.length }}</div>
            <div class="stat-label">Total Candidates</div>
          </div>
        </div>
      </div>

      <div class="candidates-section" *ngIf="candidates.length > 0">
        <h3>👥 Uploaded Candidates</h3>
        <div class="candidates-list">
          <div *ngFor="let candidate of candidates" class="candidate-item">
            <div class="candidate-name">{{ candidate.name }}</div>
          </div>
        </div>
      </div>

      <div *ngIf="candidates.length === 0" class="empty-state">
        <p>No candidates uploaded yet. Start by uploading resumes above!</p>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .header h2 {
      color: #2c3e50;
      margin-bottom: 20px;
    }

    .upload-section {
      margin-bottom: 30px;
    }

    h3 {
      color: #2c3e50;
      margin-bottom: 15px;
    }

    .upload-area {
      border: 3px dashed #007bff;
      padding: 40px;
      border-radius: 8px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s;
      background: #f0f7ff;
    }

    .upload-area:hover {
      border-color: #0056b3;
      background: #e3f2fd;
    }

    .upload-area p {
      margin: 5px 0;
      color: #666;
    }

    .file-info {
      font-size: 12px;
      color: #999;
    }

    .message {
      padding: 12px;
      margin-top: 15px;
      border-radius: 4px;
      font-size: 14px;
    }

    .message.success {
      background: #d4edda;
      color: #155724;
      border: 1px solid #c3e6cb;
    }

    .message.error {
      background: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
    }

    .progress {
      margin-top: 15px;
    }

    .progress-bar {
      background: linear-gradient(90deg, #007bff, #0056b3);
      color: white;
      padding: 10px;
      border-radius: 4px;
      text-align: center;
      font-size: 14px;
    }

    .btn-delete {
      margin-top: 15px;
      background: #dc3545;
      padding: 10px 20px;
    }

    .btn-delete:hover {
      background: #c82333;
    }

    .stats-section {
      margin: 30px 0;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
    }

    .stat-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px;
      border-radius: 8px;
      text-align: center;
    }

    .stat-value {
      font-size: 32px;
      font-weight: bold;
    }

    .stat-label {
      font-size: 14px;
      margin-top: 10px;
      opacity: 0.9;
    }

    .search-section {
      background: #f8f9fa;
      padding: 25px;
      border-radius: 8px;
      margin-bottom: 30px;
      border: 1px solid #e9ecef;
    }

    .search-section h3 {
      margin-bottom: 20px;
      color: #2c3e50;
    }

    .search-controls {
      display: grid;
      grid-template-columns: 1fr 1fr auto auto;
      gap: 15px;
      align-items: end;
    }

    .search-input-group {
      display: flex;
      flex-direction: column;
    }

    .search-input-group label {
      font-size: 13px;
      font-weight: 600;
      color: #495057;
      margin-bottom: 5px;
    }

    .search-input {
      padding: 8px 12px;
      border: 1px solid #ced4da;
      border-radius: 4px;
      font-size: 14px;
      font-family: inherit;
    }

    .search-input:focus {
      outline: none;
      border-color: #007bff;
      box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
    }

    .btn-search {
      background: #28a745;
      color: white;
      padding: 8px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 600;
      font-size: 14px;
      transition: all 0.2s;
    }

    .btn-search:hover {
      background: #218838;
    }

    .btn-clear-search {
      background: #6c757d;
      color: white;
      padding: 8px 15px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 600;
      font-size: 14px;
      transition: all 0.2s;
    }

    .btn-clear-search:hover {
      background: #5a6268;
    }

    .search-results {
      background: #fff8e1;
      padding: 20px;
      border-radius: 10px;
      margin-bottom: 30px;
      border: 1px solid #ffe082;
    }

    .search-results h3 {
      margin-bottom: 20px;
      color: #856404;
    }

    .result-item {
      display: flex;
      align-items: flex-start;
      gap: 15px;
      background: white;
      padding: 18px;
      border-radius: 8px;
      border-left: 5px solid #ffc107;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    .result-rank {
      display: flex;
      justify-content: center;
      padding-top: 2px;
    }

    .rank-badge {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      background: #ffc107;
      color: #856404;
      font-weight: bold;
      font-size: 18px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .result-info {
      flex: 1;
      min-width: 0;
    }

    .result-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }

    .result-score {
      font-size: 13px;
      color: #28a745;
      font-weight: 700;
    }

    .result-meta {
      font-size: 12px;
      color: #777;
      margin-top: 4px;
    }

    .resume-skills {
      margin-top: 14px;
      border-top: 1px solid #f0f0f0;
      padding-top: 12px;
    }

    .skills-label {
      font-size: 12px;
      font-weight: 600;
      color: #555;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .model-tag {
      font-size: 10px;
      font-weight: 500;
      background: #e8f0fe;
      color: #3c55a5;
      padding: 2px 7px;
      border-radius: 10px;
    }

    .skill-bars {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 10px 20px;
    }

    .skill-row {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .skill-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .skill-name {
      font-size: 12px;
      font-weight: 500;
      color: #2c3e50;
    }

    .skill-pct {
      font-size: 11px;
      font-weight: 700;
    }
    .skill-pct.high { color: #1e8e3e; }
    .skill-pct.mid  { color: #c97700; }
    .skill-pct.low  { color: #1565c0; }

    .skill-bar-bg {
      width: 100%;
      height: 5px;
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

    .candidates-section {
      margin-top: 30px;
    }

    .candidates-list {
      display: flex;
      flex-direction: column;
      gap: 15px;
    }

    .candidate-item {
      background: #f9f9f9;
      padding: 20px;
      border-radius: 8px;
      border-left: 5px solid #007bff;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      transition: all 0.2s;
    }

    .candidate-item:hover {
      box-shadow: 0 4px 8px rgba(0,0,0,0.15);
      transform: translateX(5px);
    }

    .candidate-name {
      font-weight: bold;
      font-size: 16px;
      color: #2c3e50;
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #999;
      font-size: 16px;
    }
  `]
})
export class DashboardComponent implements OnInit {
  candidates: Candidate[] = [];
  isUploading: boolean = false;
  uploadMessage: string = '';
  uploadSuccess: boolean = false;

  // Search properties
  searchSkills: string = '';
  searchExperience: number | null = null;
  searchResults: Candidate[] = [];
  activeSearchSkills: string[] = [];  // skills the user actually searched for

  constructor(private candidateService: CandidateService) {}

  ngOnInit(): void {
    this.loadCandidates();
  }

  loadCandidates(): void {
    this.candidateService.getCandidates().subscribe({
      next: (data) => {
        this.candidates = data;
      },
      error: (error) => {
        console.error('Error loading candidates:', error);
      }
    });
  }

  onFileSelected(event: Event): void {
    const target = event.target as HTMLInputElement;
    const files = target.files;

    if (files && files.length > 0) {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }

      this.isUploading = true;
      this.uploadMessage = '';

      this.candidateService.uploadResumes(formData).subscribe({
        next: (_response) => {
          this.uploadSuccess = true;
          this.uploadMessage = `Successfully uploaded ${files.length} resume(s)!`;
          this.isUploading = false;
          this.loadCandidates();
          target.value = '';
        },
        error: (_error) => {
          this.uploadSuccess = false;
          this.uploadMessage = _error.error?.message || 'Error uploading resumes. Please try again.';
          this.isUploading = false;
        }
      });
    }
  }

  clearCandidates(): void {
    if (confirm('Are you sure you want to delete all candidates?')) {
      this.candidateService.deleteCandidates().subscribe({
        next: () => {
          this.candidates = [];
          this.uploadMessage = 'All candidates deleted successfully!';
          this.uploadSuccess = true;
        },
        error: (_error) => {
          this.uploadMessage = 'Error deleting candidates.';
          this.uploadSuccess = false;
        }
      });
    }
  }

  performSearch(): void {
    if (!this.searchSkills && !this.searchExperience) {
      alert('Please enter skills or years of experience to search');
      return;
    }

    // Build query string from skills and experience
    let query = '';
    if (this.searchSkills) {
      query += this.searchSkills;
    }
    if (this.searchExperience) {
      query += (query ? ' ' : '') + this.searchExperience + ' years';
    }

    // Build filters
    const filters: any = {};
    if (this.searchSkills) {
      filters.skills = this.searchSkills.split(',').map((s: string) => s.trim());
    }
    if (this.searchExperience !== null && this.searchExperience !== undefined) {
      filters.minExperience = this.searchExperience;
    }

    this.candidateService.searchCandidates({
      query: query,
      filters: filters
    }).subscribe({
      next: (response) => {
        this.searchResults = response.candidates;
        // Store the skills actually searched so template can filter
        this.activeSearchSkills = this.searchSkills
          ? this.searchSkills.split(',').map((s: string) => s.trim()).filter(s => s)
          : [];
      },
      error: (_error) => {
        console.error('Error searching candidates:', _error);
        this.searchResults = [];
      }
    });
  }

  clearSearch(): void {
    this.searchResults = [];
    this.searchSkills = '';
    this.searchExperience = null;
    this.activeSearchSkills = [];
  }

  /** Return per-skill relevance % from all-MiniLM-L6-v2 */
  getSkillPct(candidate: any, skill: string): number {
    if (candidate.skill_scores && candidate.skill_scores[skill] !== undefined) {
      return candidate.skill_scores[skill];
    }
    return 0;
  }

  /**
   * Return only the candidate's skills that match what was searched.
   * Matching is case-insensitive. If no skills were searched, return all.
   */
  getMatchedSkills(candidate: any): string[] {
    const allSkills: string[] = candidate.skills || [];
    if (!this.activeSearchSkills.length) return allSkills;
    return allSkills.filter(skill =>
      this.activeSearchSkills.some(searched =>
        skill.toLowerCase().includes(searched.toLowerCase()) ||
        searched.toLowerCase().includes(skill.toLowerCase())
      )
    );
  }
}
