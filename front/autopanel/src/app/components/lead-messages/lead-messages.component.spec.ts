import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LeadMessagesComponent } from './lead-messages.component';

describe('LeadMessagesComponent', () => {
  let component: LeadMessagesComponent;
  let fixture: ComponentFixture<LeadMessagesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadMessagesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LeadMessagesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
