import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <nav class="navbar">
      <div class="container">
        <h1>🤖 Candidate Search Bot</h1>
        <div class="nav-links">
          <a routerLink="/">Dashboard</a>
          <a routerLink="/search">Search</a>
        </div>
      </div>
    </nav>
    <main>
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    .navbar {
      background-color: #2c3e50;
      color: white;
      padding: 15px 0;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    h1 {
      font-size: 24px;
      margin: 0;
    }

    .nav-links {
      display: flex;
      gap: 20px;
    }

    .nav-links a {
      color: white;
      text-decoration: none;
      font-size: 14px;
      transition: color 0.3s;
    }

    .nav-links a:hover {
      color: #3498db;
    }

    main {
      max-width: 1200px;
      margin: 20px auto;
      padding: 0 20px;
    }
  `]
})
export class AppComponent {}
