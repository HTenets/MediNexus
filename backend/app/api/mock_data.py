"""Mock data endpoints — return realistic sample data for all pages.

Used during development to verify full frontend-backend integration
before real data sources are connected.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()

# ── Shared helpers ─────────────────────────────────────────────────────── #

NOW = datetime.now(timezone.utc).isoformat()[:19]


def _symptom_based(query: str) -> str:
    q = query.lower()
    if "head" in q or "头痛" in q or "头" in q:
        return "headache"
    if "chest" in q or "胸" in q:
        return "chest_pain"
    if "fever" in q or "发热" in q or "发烧" in q:
        return "fever"
    if "cough" in q or "咳嗽" in q:
        return "cough"
    if "rash" in q or "皮疹" in q:
        return "rash"
    if "anxiety" in q or "焦虑" in q:
        return "anxiety"
    return "general"


# ── Knowledge sources (mock) ──────────────────────────────────────────── #

@router.get("/knowledge-cases")
async def mock_knowledge_cases(query: str = "cough"):
    """Return mock clinical case results for any query."""
    st = _symptom_based(query)
    cases = {
        "headache": [
            {"title": "紧张性头痛临床路径", "source": "北京协和医院", "match": "94%",
             "content": "患者女性，32岁，双侧颞部压迫性头痛2月，无恶心呕吐，无先兆。诊断：紧张性头痛。处理：放松训练+对症止痛。"},
            {"title": "偏头痛急性期治疗", "source": "华山医院", "match": "87%",
             "content": "患者男性，28岁，反复发作性单侧搏动性头痛3年，伴畏光、恶心。诊断：偏头痛（无先兆）。处理：曲普坦类药物。"},
        ],
        "chest_pain": [
            {"title": "不稳定心绞痛诊疗", "source": "阜外医院", "match": "91%",
             "content": "患者男性，55岁，胸骨后压榨感2h，向左臂放射，含服硝酸甘油缓解。诊断：不稳定心绞痛。"},
            {"title": "急性心肌梗死病例", "source": "安贞医院", "match": "85%",
             "content": "患者男性，60岁，持续胸痛伴大汗3h。ECG示V1-V4导联ST段抬高。诊断：急性前壁心梗。"},
        ],
        "fever": [
            {"title": "社区获得性肺炎", "source": "中日友好医院", "match": "92%",
             "content": "患者女性，45岁，发热(Tmax 39.2°C)伴咳嗽咳痰3天。胸片示右下肺斑片影。诊断：CAP。处理：抗生素治疗。"},
            {"title": "流感诊疗病例", "source": "北京医院", "match": "88%",
             "content": "患者男性，30岁，突发高热伴全身酸痛乏力。流感快速检测阳性。诊断：甲型流感。"},
        ],
        "cough": [
            {"title": "急性支气管炎", "source": "北京医院", "match": "93%",
             "content": "患者男性，35岁，咳嗽咳痰1周，无发热。双肺呼吸音粗。诊断：急性支气管炎。"},
        ],
        "rash": [
            {"title": "急性荨麻疹", "source": "北大人民医院", "match": "90%",
             "content": "患者女性，25岁，进食海鲜后全身红色风团伴剧烈瘙痒2h。诊断：急性荨麻疹。"},
        ],
        "anxiety": [
            {"title": "广泛性焦虑障碍", "source": "北医六院", "match": "89%",
             "content": "患者女性，35岁，过度担忧伴紧张不安6月，伴失眠心悸。GAD-7:15分。"},
        ],
    }
    return cases.get(st, [{"title": f"相关病例: {query}", "source": "临床数据库", "match": "80%",
                           "content": f"基于{query}的匹配临床病例。"}])


@router.get("/knowledge-theory")
async def mock_knowledge_theory(query: str = "cough"):
    st = _symptom_based(query)
    theory = {
        "headache": [
            {"title": "头痛诊断指南", "source": "中华医学会神经病学分会", "weight": "0.6",
             "content": "头痛诊断应区分原发性和继发性。原发性头痛包括偏头痛、紧张性头痛、丛集性头痛。"},
        ],
        "fever": [
            {"title": "发热诊疗规范", "source": "中国医师协会", "weight": "0.6",
             "content": "不明原因发热（FUO）定义为体温≥38.3°C持续≥3周，经1周住院检查仍未明确诊断。"},
        ],
    }
    return theory.get(st, [{"title": f"相关理论: {query}", "source": "医学理论库", "weight": "0.6",
                            "content": f"基于{query}的医学理论内容。"}])


@router.get("/knowledge-papers")
async def mock_knowledge_papers(query: str = "cough"):
    st = _symptom_based(query)
    papers = {
        "anxiety": [
            {"title": "Digital CBT for Anxiety Disorders", "journal": "JAMA Psychiatry 2025", "weight": "0.3",
             "content": "RCT of 1,200 patients showing digital CBT non-inferior to in-person therapy for GAD."},
        ],
        "fever": [
            {"title": "Biomarkers for Fever of Unknown Origin", "journal": "NEJM 2024", "weight": "0.3",
             "content": "Novel biomarker panel achieving AUC 0.89 for distinguishing infectious vs non-infectious FUO."},
        ],
    }
    return papers.get(st, [{"title": f"Related paper: {query}", "journal": "PubMed", "weight": "0.3",
                            "content": f"Recent research related to {query}."}])


# ── Consultation / SOAP ───────────────────────────────────────────────── #

@router.get("/consultation/{consult_id}")
async def mock_consultation(consult_id: str):
    return {
        "session_id": consult_id,
        "patient_id": "patient_demo_001",
        "status": "completed",
        "current_agent": "followup",
        "history": [
            {"role": "user", "content": "我头痛两天了，有点低烧"},
            {"role": "agent", "agent": "triage", "content": "【分诊结果】紧急度: routine | 科室: 内科"},
            {"role": "agent", "agent": "doctor", "content": "【诊断】急性上呼吸道感染"},
            {"role": "agent", "agent": "review", "content": "【审查】未发现禁忌症"},
        ],
        "soap": {
            "subjective": "头痛两天，伴低热37.8°C，无恶心呕吐",
            "objective": "体温37.8°C，咽部轻度充血",
            "assessment": "急性上呼吸道感染，紧张性头痛可能",
            "plan": "对症处理，休息补液；如高热持续需线下就医",
            "diagnosis": "急性上呼吸道感染",
        }
    }


@router.get("/records/{patient_id}")
async def mock_records(patient_id: str):
    return [
        {"id": "c001", "date": "2026-06-12", "diagnosis": "急性上呼吸道感染", "status": "completed",
         "subjective": "头痛发热3天", "assessment": "急性上呼吸道感染", "plan": "对症治疗"},
        {"id": "c002", "date": "2026-05-28", "diagnosis": "接触性皮炎", "status": "completed",
         "subjective": "面部皮疹伴瘙痒2天", "assessment": "接触性皮炎", "plan": "外用药膏"},
    ]


@router.get("/profile/{patient_id}")
async def mock_profile(patient_id: str):
    return {
        "name": "Demo User",
        "gender": "男", "age": "32",
        "allergies": ["青霉素过敏", "花粉过敏"],
        "past_illnesses": ["偏头痛史", "2型糖尿病"],
        "medications": ["二甲双胍 500mg bid"],
        "vitals": {"心率": "72 bpm", "血压": "128/82 mmHg", "血氧": "99%", "体温": "36.5°C"},
        "bio_age": {"age": "34", "actual_age": "36", "trend": "优"},
        "ai_memory": ["慢性偏头痛史（高置信度）", "倾向于清晨预约", "轻度青霉素过敏"],
    }


@router.get("/dashboard/{patient_id}")
async def mock_dashboard(patient_id: str):
    return {
        "vitals": {"心率": "62", "血压": "118/77", "血氧": "99%"},
        "bio_age": "34",
        "risks": ["偏头痛复发风险 22%", "睡眠不足趋势"],
        "ai_suggestions": ["今日保持充足饮水", "22:30前入睡"],
        "devices": ["Apple Watch 已连接", "血压计离线"],
    }


@router.get("/system-status")
async def mock_system_status():
    return {
        "overall": "healthy",
        "uptime": "99.97%",
        "services": [
            {"name": "Backend API", "status": "healthy", "latency": "24ms"},
            {"name": "PostgreSQL", "status": "healthy", "latency": "12ms"},
            {"name": "Redis", "status": "healthy", "latency": "3ms"},
            {"name": "Qdrant", "status": "healthy", "latency": "15ms"},
            {"name": "Agent Registry", "status": "healthy", "latency": "8ms"},
            {"name": "RAG Knowledge Base", "status": "degraded", "latency": "120ms"},
        ]
    }


@router.get("/patients")
async def mock_patients():
    return [
        {"id": "P001", "name": "张三", "last_visit": "2026-06-12", "status": "正常"},
        {"id": "P002", "name": "李四", "last_visit": "2026-05-28", "status": "随访中"},
        {"id": "P003", "name": "王五", "last_visit": "2026-06-01", "status": "正常"},
    ]
