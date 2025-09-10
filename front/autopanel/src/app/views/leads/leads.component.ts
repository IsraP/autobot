import { CommonModule, NgForOf } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';


@Component({
  selector: 'app-leads',
  standalone: true,
  imports: [NgForOf, CommonModule],
  templateUrl: './leads.component.html',
  styleUrl: './leads.component.scss'
})
export class LeadsComponent implements OnInit{

  session
  clientes: cliente[] = []
  conversa: mensagem[] = []
  constructor( 
      private router : Router, 
      private fb: FormBuilder,
      private http:HttpClient
    ){}
  ngOnInit(): void {
    this.session = sessionStorage.getItem("token");
    if(!this.session)
      this.router.navigate(["/login"])    

    this.obterLeads()
  }
  obterLeads(){
    const head = new HttpHeaders({
      "Authorization": `Bearer ${JSON.parse(this.session).access_token}`
    });
    var item = sessionStorage.getItem("clientes")
    if(item)
   // this.clientes = JSON.parse(item)
    this.http.get<cliente[]>("http://localhost:8000/leads?page=1",{headers:head}).subscribe((res) =>{
      console.log(res)
      sessionStorage.setItem("clientes",JSON.stringify(res))
      this.clientes = res
    })
  }
  mostrarConversa(id: any) {
  const head = new HttpHeaders({
      "Authorization": `Bearer ${JSON.parse(this.session).access_token}`
    });
    var item = sessionStorage.getItem("conversa")
    if(item)
    //this.conversa = JSON.parse(item)
    this.http.get<mensagem[]>(`http://localhost:8000/leads/${id}/interactions`,{headers:head}).subscribe((res) =>{
      console.log(res)
      sessionStorage.setItem("conversa", JSON.stringify(res))
      this.conversa = res
    })
  }
}

class cliente{
  id
  client
  last_client_message
  updated_at
  received_at
}
class mensagem{
  content
  origin
  sent_at

}
