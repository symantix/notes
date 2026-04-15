##Schoolahoop

- Interest filters:
	- Small class size: If student_teacher_ratio < 15
	- High Test Scores: test_score_rating set to "high"
	- Scholarships available: scholarships_supported has any value
	- Non-religious: religious_affiliation = "non_religious"
	- Religious: religious_affiliation is anything besides blank, NULL, or "non_religious"
	- K-12 School: school.grade_min === 0 && school.grade_max === 12