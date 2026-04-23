import { Routes } from '@angular/router';
import { CandidateSearchComponent } from './components/candidate-search/candidate-search.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'search', component: CandidateSearchComponent },
  { path: '**', redirectTo: '' }
];
