import { Component, OnInit } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent implements OnInit {

  constructor( 
    private router : Router, 
    private fb: FormBuilder
  ){
    
  }
  ngOnInit(): void {
    //throw new Error('Method not implemented.');
  }
  public login(){
    this.router.navigate(["/leads"])
  }
}
