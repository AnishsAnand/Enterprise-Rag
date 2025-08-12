
import {
  Component,
  OnInit,
  ViewChild,
  ElementRef,
  HostListener,
  AfterViewChecked,
  Input,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';
import { jwtDecode } from 'jwt-decode';
import { Router } from '@angular/router'

interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  sources?: {
    title?: string;
    url: string;
    relevance_score: number;
  }[];
}

interface KnowledgeStats {
  document_count: number;
  status: string;
  last_updated: string;
}
@Component({
  selector: 'app-rag-widget',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatCardModule,
    MatTooltipModule,
  ],
  templateUrl: './rag-widget.component.html',
  styleUrls: ['./rag-widget.component.css'],
})
export class RagWidgetComponent implements OnInit, AfterViewChecked {
  @ViewChild('chatMessages') chatMessages!: ElementRef;
  @Input() forceUserRole: 'admin' | 'user' | null = null;

  isExpanded = true;
  currentMessage = '';
  scrapeUrl = '';
  bulkScrapeUrl = '';

  isTyping = false;
  isScraping = false;
  isBulkScraping = false;

  chatHistory: ChatMessage[] = [];
  scrapeStatus: any = null;

  knowledgeStats: KnowledgeStats = {
    document_count: 0,
    status: 'unknown',
    last_updated: '',
  };
  uploading = false;
  progress = 0;
  uploadStatus = '';
  uploadError = '';
  uploadedFileName = '';
  isAdmin = true;

  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient,private router: Router) {}

  ngOnInit() {
  this.isExpanded = true;
  this.setRoleFromToken();
  this.initializeChat();
  this.refreshStats();
}

setRoleFromToken() {
  if (this.forceUserRole) {
    this.isAdmin = this.forceUserRole === 'admin';
    return;
  }

  const token = localStorage.getItem('token');
  if (!token) {
    this.isAdmin = false;
    return;
  }

  try {
    const decoded: any = jwtDecode(token);
    this.isAdmin = decoded?.role === 'admin';
  } catch (err) {
    console.error('Invalid token:', err);
    this.isAdmin = false;
  }
}

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  toggleWidget() {
    this.isExpanded = !this.isExpanded;
    if (this.isExpanded) {
      setTimeout(() => this.scrollToBottom(), 150);
    }
  }

  logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }

  initializeChat() {
    const welcomemessage = this.isAdmin ? 'Welcome, Admin!' : 'Welcome User !';
    this.chatHistory = [
      {
        id: 'welcome-bot',
        type: 'bot',
        content:welcomemessage,
        timestamp: new Date(),
      },
    ];
  }

  async sendMessage() {
    const trimmed = this.currentMessage.trim();
    if (!trimmed) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: trimmed,
      timestamp: new Date(),
    };
    this.chatHistory.push(userMessage);
    this.currentMessage = '';
    this.isTyping = true;

    try {
      const response = await this.http
        .post<any>(`${this.apiUrl}/rag-widget/widget/query`, {
          query: trimmed,
          max_results: 5,
          include_sources: true,
        })
        .toPromise();

      const botMessage: ChatMessage = {
        id: Date.now().toString() + '_bot',
        type: 'bot',
        content: response.answer || 'No response received.',
        timestamp: new Date(),
        sources: response.sources || [],
      };
      this.chatHistory.push(botMessage);
    } catch (error) {
      this.chatHistory.push({
        id: Date.now().toString() + '_error',
        type: 'bot',
        content:
          'Error while processing your question. Check if backend is running or try again later.',
        timestamp: new Date(),
      });
    }

    this.isTyping = false;
  }

  async scrapeSingleUrl() {
    if (!this.scrapeUrl) return;
    this.isScraping = true;
    this.scrapeStatus = null;

    try {
      const response = await this.http
        .post<any>(`${this.apiUrl}/rag-widget/widget/scrape`, {
          url: this.scrapeUrl,
          store_in_knowledge: true,
        })
        .toPromise();

      this.scrapeStatus = {
        title: 'Scraping Successful!',
        message: `Scraped "${response.title}" and added to knowledge base.`,
        details: `Content length: ${response.content_length}, Method: ${response.method_used}`,
      };
      this.scrapeUrl = '';
      this.refreshStats();
    } catch (error: any) {
      this.scrapeStatus = {
        title: 'Scraping Failed',
        message:
          error?.error?.detail || 'Unable to scrape URL. Please check and retry.',
      };
    }

    this.isScraping = false;
  }

  async bulkScrape() {
    if (!this.bulkScrapeUrl) return;
    this.isBulkScraping = true;
    this.scrapeStatus = null;

    try {
      const response = await this.http
        .post<any>(`${this.apiUrl}/rag-widget/widget/bulk-scrape`, {
          base_url: this.bulkScrapeUrl,
          max_depth: 2,
          max_urls: 50,
          auto_store: true,
        })
        .toPromise();

      this.scrapeStatus = {
        title: 'Bulk Scraping Started!',
        message: `Discovered ${response.discovered_urls_count} URLs.`,
        details: `Estimated time: ${response.estimated_time}`,
      };
      this.bulkScrapeUrl = '';

      setTimeout(() => this.refreshStats(), 10000);
    } catch (error: any) {
      this.scrapeStatus = {
        title: 'Bulk Scraping Failed',
        message:
          error?.error?.detail || 'Failed to bulk scrape. Check base URL.',
      };
    }

    this.isBulkScraping = false;
  }

  async refreshStats() {
    try {
      const stats = await this.http
        .get<KnowledgeStats>(`${this.apiUrl}/rag-widget/widget/knowledge-stats`)
        .toPromise();
      this.knowledgeStats = stats!;
    } catch (error) {
      console.error('Failed to load knowledge stats.');
    }
  }

  async clearKnowledge() {
    if (!confirm('Are you sure you want to clear the knowledge base?')) return;

    try {
      await this.http
        .delete(`${this.apiUrl}/rag-widget/widget/clear-knowledge`)
        .toPromise();

      this.knowledgeStats = {
        document_count: 0,
        status: 'cleared',
        last_updated: '',
      };

      this.chatHistory.push({
        id: Date.now().toString(),
        type: 'bot',
        content: 'Knowledge base cleared. You can now scrape fresh content.',
        timestamp: new Date(),
      });
    } catch (error) {
      alert('Failed to clear knowledge base.');
    }
  }

  scrollToBottom() {
    try {
      const el = this.chatMessages?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    } catch (err) {}
  }

  @HostListener('document:keydown.escape', ['$event'])
  onEscapeKey() {
    if (this.isExpanded) {
      this.toggleWidget();
    }
  }

  handleFileInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.uploadFile(input.files[0]);
    }
  }

  handleDrop(event: DragEvent): void {
    event.preventDefault();
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.uploadFile(event.dataTransfer.files[0]);
    }
  }

  allowDrop(event: DragEvent): void {
    event.preventDefault();
  }
  get isLoginPage(): boolean {
    return this.router.url.includes('/login');
  }

  uploadFile(file: File): void {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('store_in_knowledge', 'true');

    this.uploading = true;
    this.progress = 0;
    this.uploadStatus = '';
    this.uploadError = '';
    this.uploadedFileName = file.name;

    this.http
      .post<any>(`${this.apiUrl}/rag-widget/widget/upload-file`, formData, {
        reportProgress: true,
        observe: 'events',
      })
      .subscribe({
        next: (event: any) => {
          if (event.type === 1 && event.total) {
            this.progress = Math.round((100 * event.loaded) / event.total);
          } else if (event.type === 4) {
            this.uploadStatus = `Uploaded: ${event.body.filename} (${event.body.format})`;
            this.refreshStats();
            this.uploading = false;
          }
        },
        error: (err) => {
          this.uploadError = 'Upload failed: ' + (err.error?.detail || err.message);
          this.uploading = false;
        },
      });
  }
}
