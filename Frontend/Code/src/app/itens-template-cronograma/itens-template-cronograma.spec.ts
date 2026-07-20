import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ItensTemplateCronograma } from './itens-template-cronograma';

describe('ItensTemplateCronograma', () => {
  let component: ItensTemplateCronograma;
  let fixture: ComponentFixture<ItensTemplateCronograma>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ItensTemplateCronograma],
    }).compileComponents();

    fixture = TestBed.createComponent(ItensTemplateCronograma);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
