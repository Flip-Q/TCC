import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Substituicoes } from './substituicoes';

describe('Substituicoes', () => {
  let component: Substituicoes;
  let fixture: ComponentFixture<Substituicoes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Substituicoes],
    }).compileComponents();

    fixture = TestBed.createComponent(Substituicoes);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
