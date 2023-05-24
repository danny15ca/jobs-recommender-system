import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@auth0/auth0-angular';

import { JobsComponent } from './jobs/jobs.component';
import { SignInComponent } from './sign-in/sign-in.component';

const routes: Routes = [
  {
    path: '',
    redirectTo: 'signIn',
    pathMatch: 'full',
  },
  {
    path: 'jobs',
    component: JobsComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'signIn',
    component: SignInComponent,
  },
  {
    path: '**',
    redirectTo: 'signIn',
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
