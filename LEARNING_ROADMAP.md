# SkillScope Learning Roadmap — Trevor Reeves

**Current level:** Mid-level C#/.NET Engineer
**Target:** Senior .NET / Azure Engineer (then Architect track)
**Generated from:** 231 jobs, 224 skills, 29 niches analyzed

---

## Month 1-2: Close the Azure Gap (Highest ROI)

**Why first:** Azure appears as a gap in 25/29 niches. It's the #1 thing holding back your .NET career. Every .NET job above $170k expects Azure.

### Skills to learn:
| Skill | Salary Impact | How to Prove |
|-------|--------------|-------------|
| **Azure App Service** | $195k avg (+8.2%) | Deploy DemonsAndDogs API to Azure |
| **Azure SQL / Cosmos DB** | Part of Azure | Migrate PostgreSQL to Azure SQL or keep PG on Azure |
| **Azure DevOps** | Part of Azure | Set up pipelines (or keep GitHub Actions — both valid) |
| **Azure AD / Entra ID** | Part of Azure | Add auth to DemonsAndDogs |

### Action plan:
- [ ] Week 1-2: Get Azure free tier, do Microsoft Learn "Azure Fundamentals" (AZ-900 path)
- [ ] Week 3-4: Deploy DemonsAndDogs API to Azure App Service
- [ ] Week 5-6: Set up Azure SQL or Azure Database for PostgreSQL
- [ ] Week 7-8: Add CI/CD from GitHub Actions → Azure deployment
- [ ] **Proof artifact:** demonsanddogs.com now points to a live Azure deployment
- [ ] **Cert (optional but high-signal):** AZ-900 Azure Fundamentals (easy, looks good on LinkedIn)

---

## Month 2-3: Kubernetes + Terraform (Unlock 24 Niches)

**Why second:** Kubernetes is the #1 gap across 24/29 niches. Combined with Terraform, it unlocks DevOps, Platform Engineering, Cloud Architecture, and SRE paths.

### Skills to learn:
| Skill | Salary Impact | How to Prove |
|-------|--------------|-------------|
| **Kubernetes** | $196k avg (+8.8%) | Deploy DemonsAndDogs to AKS |
| **Terraform** | $190k avg (+5.7%) | Write IaC for the entire Azure infra |
| **Infrastructure as Code** | $181k avg (+0.7%) | Terraform IS IaC — same thing |

### Action plan:
- [ ] Week 1: Docker Compose → Kubernetes concepts (pods, services, deployments)
- [ ] Week 2-3: Write K8s manifests for DemonsAndDogs (API, Player app, Builder app, PostgreSQL)
- [ ] Week 3-4: Deploy to AKS (Azure Kubernetes Service)
- [ ] Week 5-6: Learn Terraform basics, write Azure infra as code
- [ ] Week 7-8: Full Terraform → AKS pipeline: `terraform apply` creates everything
- [ ] **Proof artifact:** DemonsAndDogs runs on AKS, infra defined in Terraform, all in the repo

---

## Month 3-5: Microservices + Event-Driven (Architecture Skills)

**Why third:** This is what separates mid from senior. Microservices ($210k, +16.7%) and System Design ($215k, +19.2%) are the highest-paying technical skills in the dataset.

### Skills to learn:
| Skill | Salary Impact | How to Prove |
|-------|--------------|-------------|
| **Microservices** | $210k avg (+16.7%) | Refactor DemonsAndDogs into services |
| **Event-Driven Architecture** | $186k avg (+3.4%) | SignalR → Azure Service Bus |
| **Kafka or Azure Service Bus** | $188k avg (+4.1%) | Add messaging between services |
| **gRPC** | $177k avg (-1.9%) | Service-to-service communication |
| **CQRS** | Architecture pattern | Separate read/write models |

### Action plan:
- [ ] Week 1-2: Study microservices patterns (Sam Newman's book or equivalent)
- [ ] Week 3-6: Split DemonsAndDogs: Campaign API, Session API, Wiki API, AI Narration service
- [ ] Week 5-8: Add Azure Service Bus or Kafka between services
- [ ] Week 7-8: Implement CQRS for at least one domain (e.g., campaign reads vs writes)
- [ ] **Proof artifact:** DemonsAndDogs architecture diagram on demonsanddogs.com showing microservices

---

## Month 5-7: AI Integration (The Differentiator)

**Why fourth:** You already have the foundation (LLM narration in DemonsAndDogs, NLP in SkillScope). Formalizing this makes you the rare ".NET engineer who does AI."

### Skills to learn:
| Skill | Salary Impact | How to Prove |
|-------|--------------|-------------|
| **Semantic Kernel** | .NET AI SDK | Upgrade DemonsAndDogs AI from raw HTTP to SK |
| **RAG pattern** | AI architecture | Add context-aware narration using campaign data |
| **Azure OpenAI Service** | Premium cloud AI | Move from local LM Studio to Azure OpenAI |
| **Vector Database (pgvector)** | Embeddings store | You already have pgvector in DemonsAndDogs |

### Action plan:
- [ ] Week 1-2: Learn Microsoft Semantic Kernel SDK
- [ ] Week 3-4: Replace LM Studio HTTP calls with Semantic Kernel in DemonsAndDogs
- [ ] Week 5-6: Implement RAG — narration uses campaign wiki/lore as context
- [ ] Week 7-8: Deploy with Azure OpenAI Service
- [ ] **Proof artifact:** DemonsAndDogs AI narration powered by Semantic Kernel + RAG + Azure OpenAI

---

## Month 7-9: Soft Skills + Visibility (The Senior Multiplier)

**Why fifth:** The data is clear — Leadership ($228k, +26.3%), Mentoring ($211k, +17.3%), and Technical Writing ($167k) are in the top skills by salary. You need to SHOW these, not just claim them.

### Skills to prove:
| Skill | Salary Impact | How to Prove |
|-------|--------------|-------------|
| **Technical Writing** | $167k avg | Blog series on building DemonsAndDogs |
| **Mentoring** | $211k avg (+17.3%) | Mentor on ADPList or at work, get testimonials |
| **Design Patterns** | Architecture knowledge | Write about patterns used in your projects |
| **Presentation Skills** | $223k avg (+24.0%) | Speak at local .NET meetup or record YouTube |

### Action plan:
- [ ] Start a blog (dev.to or personal site): "Building a Real-Time RPG Platform in .NET"
- [ ] Write 1 article per month about your architecture decisions
- [ ] Give 1 talk at a meetup or user group (virtual counts)
- [ ] LinkedIn posts about what you're building (weekly)
- [ ] Open-source a Roslyn analyzer (niche differentiator)
- [ ] **Proof artifact:** Public writing portfolio + speaking + open-source contributions

---

## Month 9-12: Specialize + Position (Senior Ready)

By now you have:
- Azure deployment (proven)
- Kubernetes + Terraform (proven)
- Microservices architecture (proven)
- AI/ML integration (proven)
- Technical writing + community presence (proven)
- Two public projects (DemonsAndDogs + SkillScope)

### Final moves:
- [ ] Update LinkedIn with data-driven headline from SkillScope
- [ ] Apply for Senior .NET / Azure Engineer roles
- [ ] Consider AZ-204 (Azure Developer Associate) cert
- [ ] Target: $160k-$200k range

---

## The Compound Effect

```
Month 0 (now):
  Mid-level C#/.NET dev, 29 skills, 42% .NET niche fit
  Salary range: $120-150k

Month 6:
  + Azure + Kubernetes + Terraform + Microservices
  .NET niche fit: ~85%
  Salary range: $150-180k

Month 12:
  + AI/Semantic Kernel + Technical Writing + Community
  .NET niche fit: ~95%
  Salary range: $170-210k
  Niches unlocked: 20+ of 29 at >70% fit
```

---

*Generated by SkillScope from 231 real job postings across RemoteOK, We Work Remotely, Hacker News, and curated .NET ecosystem data.*
