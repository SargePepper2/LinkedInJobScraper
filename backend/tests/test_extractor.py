"""Tests for the skill extraction engine."""

from app.services.extractor import SkillExtractor


def test_exact_match():
    extractor = SkillExtractor()
    results = extractor.extract("We need someone with Python and React experience.")
    names = {r.name for r in results}
    assert "Python" in names
    assert "React" in names


def test_alias_match():
    extractor = SkillExtractor()
    results = extractor.extract("Must know JS and K8s")
    names = {r.name for r in results}
    assert "JavaScript" in names
    assert "Kubernetes" in names


def test_special_char_skills():
    extractor = SkillExtractor()
    results = extractor.extract("Experience with C++ and .NET framework required")
    names = {r.name for r in results}
    assert "C++" in names
    assert ".NET" in names


def test_context_detection():
    extractor = SkillExtractor()
    results = extractor.extract("5+ years of experience with Python")
    names = {r.name for r in results}
    assert "Python" in names


def test_no_false_positives():
    extractor = SkillExtractor()
    results = extractor.extract("Looking for a friendly team player who enjoys lunch.")
    # Should not match random words as skills
    names = {r.name for r in results}
    assert "Python" not in names
    assert "React" not in names


def test_comprehensive_job_description():
    extractor = SkillExtractor()
    text = """
    Senior Full-Stack Engineer

    Requirements:
    - 5+ years with TypeScript and React
    - Experience with Node.js, PostgreSQL, and Redis
    - Familiar with AWS (EC2, S3, Lambda)
    - Knowledge of Docker and Kubernetes
    - CI/CD pipelines with GitHub Actions
    - Agile/Scrum methodology
    """
    results = extractor.extract(text)
    names = {r.name for r in results}
    assert "TypeScript" in names
    assert "React" in names
    assert "Node.js" in names
    assert "PostgreSQL" in names
    assert "Redis" in names
    assert "AWS" in names
    assert "Docker" in names
    assert "Kubernetes" in names


def test_deduplication():
    extractor = SkillExtractor()
    # "JS" is an alias for JavaScript, should only appear once
    results = extractor.extract("We use JavaScript and JS daily")
    js_matches = [r for r in results if r.name == "JavaScript"]
    assert len(js_matches) == 1
