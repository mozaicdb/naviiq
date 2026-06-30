CAREER_CATEGORIES_CAREER = [
    "Software Development",
    "UI/UX and Product Design",
    "Data Analysis and Business Intelligence",
    "Digital Marketing and Content Creation",
    "Graphic Design and Visual Branding",
    "AgriTech and Digital Agriculture",
    "HealthTech and Digital Health",
    "FinTech and Digital Finance",
    "EdTech and Digital Learning",
    "Construction Tech, BIM and 3D Visualization",
    "Architecture and Digital Design",
    "LegalTech and Digital Compliance",
    "Video Editing and Motion Graphics",
    "Cybersecurity",
    "Cloud and DevOps",
    "Project Management and Digital Operations",
    "Freelance and Digital Entrepreneurship",
    "Artificial Intelligence and Machine Learning",
    "Blockchain and Web3",
]

CAREER_CATEGORIES_DISCOVERY = [
    "Technology and Software",
    "Design and Creativity",
    "Data and Analysis",
    "Business and Marketing",
    "Healthcare and Science",
    "Education and Teaching",
    "Agriculture and Environment",
    "Construction and Engineering",
    "Media and Content Creation",
]

CAREER_CATEGORIES_EXPLORER = [
    "Technology",
    "Design",
    "Business",
    "Science and Healthcare",
    "Education",
    "Creative and Media",
]

REASONING_INSTRUCTIONS = """
When matching a student to a career category, follow these rules strictly:

1. Start with the student's existing profession or background. This is the foundation, never ignore it.
2. Then consider their stated interest. The interest decides the direction inside that foundation, it does not replace the foundation.
3. Look for the category that blends both the profession and the interest together.
4. Never default to Software Development unless the student's background or interest is genuinely software engineering or programming.
5. If no category in the list is an exact match, you are allowed to combine or rename categories to create a more accurate specific match. For example, a nurse interested in content creation should become "Health Content Creation," not be forced into an unrelated existing category.
6. If the student's profession has no close category at all (for example farming, teaching, or law), build a reasonable blended category name yourself using the same naming style as the list, instead of forcing the closest unrelated option.
7. Always explain briefly why the chosen category fits both their background and their interest, do not just state the category name.
8. Do not invent unrelated or vague categories. The blended name must clearly relate to the student's real profession and stated interest.
"""


def get_categories_for_mode(student_mode):
    if student_mode == "career":
        return CAREER_CATEGORIES_CAREER
    elif student_mode == "discovery":
        return CAREER_CATEGORIES_DISCOVERY
    elif student_mode == "explorer":
        return CAREER_CATEGORIES_EXPLORER
    else:
        return CAREER_CATEGORIES_CAREER