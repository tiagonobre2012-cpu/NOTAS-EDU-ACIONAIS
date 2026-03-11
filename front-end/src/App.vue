<script setup>
import { computed, onMounted, reactive, ref } from "vue";

const API_BASE = "http://127.0.0.1:8000";

const loading = ref(false);
const message = ref("");

const classrooms = ref([]);
const subjects = ref([]);
const students = ref([]);
const gradeRecords = ref([]);

const form = reactive({
  classroomName: "",
  subjectName: "",
  studentName: "",
  selectedClassroomId: "",
  selectedSubjectId: "",
});

const gradeDraft = reactive({});

const selectedClassroomIdNumber = computed(() => Number(form.selectedClassroomId || 0));
const selectedSubjectIdNumber = computed(() => Number(form.selectedSubjectId || 0));

function statusLabel(status) {
  if (status === "APPROVED") return "Aprovado";
  if (status === "RECOVERY") return "Recuperacao";
  if (status === "FAILED") return "Reprovado";
  return status;
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Erro na API");
  }

  if (response.status === 204) return null;
  return response.json();
}

function ensureDraft(studentId) {
  if (!gradeDraft[studentId]) {
    gradeDraft[studentId] = {
      note_1: null,
      note_2: null,
      note_3: null,
      recovery_note: null,
    };
  }
}

async function loadBasics() {
  loading.value = true;
  message.value = "";
  try {
    const [classroomsResp, subjectsResp] = await Promise.all([
      api("/classrooms"),
      api("/subjects"),
    ]);
    classrooms.value = classroomsResp;
    subjects.value = subjectsResp;

    if (!form.selectedClassroomId && classrooms.value.length > 0) {
      form.selectedClassroomId = String(classrooms.value[0].id);
    }
    if (!form.selectedSubjectId && subjects.value.length > 0) {
      form.selectedSubjectId = String(subjects.value[0].id);
    }

    await loadStudents();
    await loadGradeRecords();
  } catch (err) {
    message.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function loadStudents() {
  if (!selectedClassroomIdNumber.value) {
    students.value = [];
    return;
  }
  students.value = await api(`/students?classroom_id=${selectedClassroomIdNumber.value}`);
  for (const student of students.value) {
    ensureDraft(student.id);
  }
}

async function loadGradeRecords() {
  if (!selectedClassroomIdNumber.value || !selectedSubjectIdNumber.value) {
    gradeRecords.value = [];
    return;
  }

  gradeRecords.value = await api(
    `/grade-records?classroom_id=${selectedClassroomIdNumber.value}&subject_id=${selectedSubjectIdNumber.value}`,
  );

  for (const row of gradeRecords.value) {
    gradeDraft[row.student_id] = {
      note_1: row.note_1,
      note_2: row.note_2,
      note_3: row.note_3,
      recovery_note: row.recovery_note,
    };
  }
}

async function createClassroom() {
  if (!form.classroomName.trim()) return;
  try {
    const created = await api("/classrooms", {
      method: "POST",
      body: JSON.stringify({ name: form.classroomName }),
    });
    form.classroomName = "";
    message.value = `Turma criada: ${created.name}`;
    await loadBasics();
  } catch (err) {
    message.value = err.message;
  }
}

async function createSubject() {
  if (!form.subjectName.trim()) return;
  try {
    const created = await api("/subjects", {
      method: "POST",
      body: JSON.stringify({ name: form.subjectName }),
    });
    form.subjectName = "";
    message.value = `Disciplina criada: ${created.name}`;
    await loadBasics();
  } catch (err) {
    message.value = err.message;
  }
}

async function createStudent() {
  if (!form.studentName.trim() || !selectedClassroomIdNumber.value) return;
  try {
    const created = await api("/students", {
      method: "POST",
      body: JSON.stringify({
        name: form.studentName,
        classroom_id: selectedClassroomIdNumber.value,
      }),
    });
    form.studentName = "";
    message.value = `Aluno criado: ${created.name}`;
    await loadStudents();
  } catch (err) {
    message.value = err.message;
  }
}

async function ensureGradeRecord(studentId) {
  const exists = gradeRecords.value.find((r) => r.student_id === studentId);
  if (exists) return exists.id;

  const created = await api("/grade-records", {
    method: "POST",
    body: JSON.stringify({
      student_id: studentId,
      classroom_id: selectedClassroomIdNumber.value,
      subject_id: selectedSubjectIdNumber.value,
      note_1: null,
      note_2: null,
      note_3: null,
      recovery_note: null,
    }),
  });

  await loadGradeRecords();
  return created.id;
}

async function saveRow(studentId) {
  if (!selectedClassroomIdNumber.value || !selectedSubjectIdNumber.value) {
    message.value = "Selecione turma e disciplina";
    return;
  }

  try {
    const gradeRecordId = await ensureGradeRecord(studentId);
    const row = gradeDraft[studentId] || {};

    await api(`/grade-records/${gradeRecordId}`, {
      method: "PUT",
      body: JSON.stringify({
        note_1: row.note_1 === "" ? null : row.note_1,
        note_2: row.note_2 === "" ? null : row.note_2,
        note_3: row.note_3 === "" ? null : row.note_3,
        recovery_note: row.recovery_note === "" ? null : row.recovery_note,
      }),
    });

    message.value = "Notas salvas";
    await loadGradeRecords();
  } catch (err) {
    message.value = err.message;
  }
}

function gradeByStudent(studentId) {
  return gradeRecords.value.find((row) => row.student_id === studentId);
}

onMounted(loadBasics);
</script>

<template>
  <main class="container">
    <h1>Diario de Classe</h1>
    <p class="subtitle">FastAPI + Vue 3 com persistencia em banco SQLite</p>

    <section class="card">
      <div class="grid">
        <div>
          <label>Nova turma</label>
          <input v-model="form.classroomName" placeholder="Ex: 3 ANO B" />
        </div>
        <div>
          <label>Nova disciplina</label>
          <input v-model="form.subjectName" placeholder="Ex: HISTORIA" />
        </div>
        <div>
          <label>Aluno</label>
          <input v-model="form.studentName" placeholder="Nome do aluno" />
        </div>
      </div>
      <div class="grid" style="margin-top: 10px">
        <button @click="createClassroom">Salvar turma</button>
        <button @click="createSubject">Salvar disciplina</button>
        <button @click="createStudent" :disabled="!selectedClassroomIdNumber">Salvar aluno</button>
      </div>
    </section>

    <section class="card">
      <div class="grid">
        <div>
          <label>Turma ativa</label>
          <select v-model="form.selectedClassroomId" @change="loadStudents(); loadGradeRecords()">
            <option v-for="classroom in classrooms" :key="classroom.id" :value="String(classroom.id)">
              {{ classroom.name }}
            </option>
          </select>
        </div>
        <div>
          <label>Disciplina ativa</label>
          <select v-model="form.selectedSubjectId" @change="loadGradeRecords">
            <option v-for="subject in subjects" :key="subject.id" :value="String(subject.id)">
              {{ subject.name }}
            </option>
          </select>
        </div>
      </div>
      <p class="small" v-if="message">{{ message }}</p>
      <p class="small" v-if="loading">Carregando...</p>
    </section>

    <section class="card table-wrap">
      <h3>Lancamento de notas</h3>
      <table>
        <thead>
          <tr>
            <th>Aluno</th>
            <th>Nota 1</th>
            <th>Nota 2</th>
            <th>Nota 3</th>
            <th>Recuperacao</th>
            <th>Media</th>
            <th>Status</th>
            <th>Acao</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in students" :key="student.id">
            <td>{{ student.name }}</td>
            <td>
              <input type="number" min="0" max="10" step="0.1" v-model.number="gradeDraft[student.id].note_1" />
            </td>
            <td>
              <input type="number" min="0" max="10" step="0.1" v-model.number="gradeDraft[student.id].note_2" />
            </td>
            <td>
              <input type="number" min="0" max="10" step="0.1" v-model.number="gradeDraft[student.id].note_3" />
            </td>
            <td>
              <input
                type="number"
                min="0"
                max="10"
                step="0.1"
                v-model.number="gradeDraft[student.id].recovery_note"
              />
            </td>
            <td>{{ gradeByStudent(student.id)?.average ?? 0 }}</td>
            <td :class="`status-${gradeByStudent(student.id)?.status}`">
              {{ statusLabel(gradeByStudent(student.id)?.status ?? "PENDING") }}
            </td>
            <td>
              <button @click="saveRow(student.id)">Salvar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>
