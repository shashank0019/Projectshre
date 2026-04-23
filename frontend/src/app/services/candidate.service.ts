import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Candidate, SearchQuery, SearchResponse } from '../models/candidate.model';

@Injectable({
  providedIn: 'root'
})
export class CandidateService {
  private apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) {}

  uploadResumes(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/candidates/upload`, formData);
  }

  searchCandidates(query: SearchQuery): Observable<SearchResponse> {
    return this.http.post<SearchResponse>(`${this.apiUrl}/candidates/search`, query);
  }

  getCandidates(): Observable<Candidate[]> {
    return this.http.get<Candidate[]>(`${this.apiUrl}/candidates`);
  }

  getCandidateById(id: string): Observable<Candidate> {
    return this.http.get<Candidate>(`${this.apiUrl}/candidates/${id}`);
  }

  deleteCandidates(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/candidates`);
  }
}
