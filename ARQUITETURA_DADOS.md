# Arquitetura de dados (explicacao simples)

Imagine uma escola com 4 cadernos principais:

1. `classrooms` (turmas): guarda nome da turma.
2. `subjects` (disciplinas): guarda nome da materia.
3. `students` (alunos): guarda nome do aluno e em qual turma ele esta.
4. `grade_records` (boletim): guarda as notas do aluno em uma disciplina.

## Relacao entre os cadernos

- Uma turma tem varios alunos.
- Uma disciplina pode aparecer para varios alunos.
- Cada linha de boletim liga: aluno + turma + disciplina.

## Campos importantes no boletim

- `note_1`, `note_2`, `note_3`: notas normais dos periodos
- `recovery_note`: nota de recuperacao (opcional)
- `average`: media final calculada automaticamente
- `status`: resultado final

## Regra de calculo

- Se tiver `recovery_note`, ela vira a media final.
- Senao, a media final e a media de `note_1`, `note_2`, `note_3`.
- Status:
  - media < 6 => `FAILED`
  - media >= 6 e < 8 => `RECOVERY`
  - media >= 8 => `APPROVED`

## Por que essa arquitetura e boa?

- Evita dados repetidos (turma e disciplina ficam separadas).
- Facilita consultas e relatorios.
- E simples de evoluir (ex: adicionar frequencia, professor, ano letivo).
