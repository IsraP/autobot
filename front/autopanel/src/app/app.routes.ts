import { Routes } from '@angular/router';
import { LoginComponent } from './views/login/login.component';
import { LeadsComponent } from './views/leads/leads.component';

export const routes: Routes = [
    {path:"", redirectTo:"/leads" , pathMatch: 'full'},
    {path:"login", component: LoginComponent },
    {path:"leads", component: LeadsComponent },
    {path:"**", redirectTo:"/leads"},

];  