import { CommonModule, NgForOf } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormsModule } from '@angular/forms';
import { Router } from '@angular/router';


@Component({
  selector: 'app-leads',
  standalone: true,
  imports: [NgForOf, CommonModule,FormsModule],
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
  mensagemAberta;
  mensagemGerada;
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
    //if(item)
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
    this.mensagemAberta=id;
    //if(item)
    //this.conversa = JSON.parse(item)
    this.http.get<mensagem[]>(`http://localhost:8000/leads/${id}/interactions`,{headers:head}).subscribe((res) =>{
      console.log(res)
      sessionStorage.setItem("conversa", JSON.stringify(res))
      this.conversa = res
    })
  }
  mensagemGeradaTexto
  GerarMensagem() {
    const head = new HttpHeaders({
      "Authorization": `Bearer ${JSON.parse(this.session).access_token}`
    });
    this.http.post<mensagem[]>(`http://localhost:8000/leads/${this.mensagemAberta}/interactions/draft`,{headers:head}).subscribe((res) =>{
      console.log(res)
      if (res && res.length > 0) {
        this.mensagemGeradaTexto = res[0].content;
      }
      sessionStorage.setItem("mensagemGerada", JSON.stringify(res))
      this.mensagemGerada = res
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
