import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
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
    private fb: FormBuilder,
    private http:HttpClient
  ){
    
  }
  formGroup: FormGroup = new FormGroup({});
  ngOnInit(): void {
    if(sessionStorage.getItem("token"))
      this.router.navigate(["/leads"])
    this.formGroup = this.fb.group({
      user:this.fb.control(""),
      password: this.fb.control("")
    })
  }
  login(){
    this.request();
    
  }
  request(){
    var url = "http://localhost:8000/token";
    var formData = new FormData();
    var user = this.formGroup.get("user")?.value
    var pwd = this.formGroup.get("password")?.value
    formData.append('username', user); // Append a simple text field
    formData.append('password',pwd  );
    this.http.post(url,formData).subscribe(res=>{
      sessionStorage.setItem("token",JSON.stringify(res))
      this.router.navigate(["/leads"])
    })
  }
}
