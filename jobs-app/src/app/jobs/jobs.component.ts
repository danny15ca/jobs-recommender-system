import { Component, OnInit, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { AuthService } from '@auth0/auth0-angular';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-jobs',
  templateUrl: './jobs.component.html',
  styleUrls: ['./jobs.component.scss']
})
export class JobsComponent implements OnInit {

  userData = {
    user_skills: '',
    user_education_level: '',
    user_experience_level: '',
    top_k: 0
  };
  recommendedJobs: any | null = null;
  displayStyle = "none";
  @ViewChild("errorMessage") errorMessage: ElementRef;

  constructor(private authService: AuthService,
              private http: HttpClient) {}

  public ngOnInit(): void {}

  onSubmit() {
    const URL = "http://127.0.0.1:8000/api/recommend";
    const data = {
      user_skills: this.userData.user_skills,
      user_education_level: this.userData.user_education_level,
      user_experience_level: this.userData.user_experience_level,
      top_k: this.userData.top_k
    };

    // Checking if user selected a valid option of number of recommended jobs
    const kValues = [1, 5, 10, 15];
    let availability = kValues.some((arrVal) => this.userData.top_k == arrVal);
    if (availability == false) { // if not, display an alert box
      this.displayStyle = "block";
      this.errorMessage.nativeElement.innerHTML = "Please select a valid number of recommended jobs.";
    } else { // if yes, verify if user's input has any blank field
      let inValidSkills = this.userData.user_skills.length == 0;
      let inValidEducationLevel = this.userData.user_education_level.length == 0;
      let inValidExperienceLevel = this.userData.user_experience_level.length == 0;
      if (inValidSkills || inValidEducationLevel || inValidExperienceLevel) { // if yes, display a relevant error message
        this.displayStyle = "block";
        this.errorMessage.nativeElement.innerHTML = "Please check your input and try again.";
      } else { // if no, proceed with REST API call
        this.http.post<any>(URL, data).subscribe(
          response => {
            this.recommendedJobs = response;
          },
          error => {
            console.log(error);
          }
        );
      }
    }
  }

  closePopup() {
    this.displayStyle = "none";
  }

}
