import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CronogramaTurma } from './cronograma-turma';

describe('CronogramaTurma', () => {
  let component: CronogramaTurma;
  let fixture: ComponentFixture<CronogramaTurma>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CronogramaTurma],
    }).compileComponents();

    fixture = TestBed.createComponent(CronogramaTurma);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
