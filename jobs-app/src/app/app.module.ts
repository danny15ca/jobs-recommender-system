import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { SignInComponent } from './sign-in/sign-in.component';
import { JobsComponent } from './jobs/jobs.component';

import { AuthModule } from '@auth0/auth0-angular';

import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [
    AppComponent,
    SignInComponent,
    JobsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    AuthModule.forRoot({
      domain: 'dev-7moiph3ly5ehuign.us.auth0.com',
      clientId: 'arrrXns3fwScV9Tv9AL3KErk7AxhVNkM',
      authorizationParams: {
        redirect_uri: "http://localhost:4200/jobs",
      },
    }),
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
