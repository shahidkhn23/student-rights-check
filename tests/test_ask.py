import json
from pathlib import Path

import pytest

from rightscheck.ask import RightsIndex, answer

INDEX = RightsIndex()
KB = json.loads((Path(__file__).resolve().parents[1] / "knowledge_base" / "laws.json").read_text())


@pytest.mark.parametrize("question,expected", [
    ("I was sick on my exam day, what can I do?", "exam_sick_withdrawal"),
    ("My landlord came into my room without asking", "landlord_entry"),
    ("How many days can I work as a non-EU student?", "intl_work_days"),
    ("There are cockroaches in my flat", "rent_reduction"),
    ("Can I get my tax back from my student job?", "tax_refund"),
    ("Do I get minimum wage in an internship?", "internship_wage"),
    ("How many hours can a Werkstudent work?", "werkstudent_20h"),
    ("Mein Vermieter will die Miete erhöhen", "rent_increase_cap"),
    ("I want to return something I bought on Amazon", "withdrawal_online"),
    ("I got an Abmahnung for a torrent", "abmahnung_cap"),
    ("A landlord rejected me because of my foreign name", "discrimination_housing"),
    ("Until when can I stay in my parents' health insurance?", "health_insurance"),
    ("Do I have to pay the Rundfunkbeitrag?", "broadcast_fee"),
    ("I failed an exam and think the grade is wrong", "exam_appeal"),
    ("Do I have to paint the walls when I move out?", "cosmetic_repairs"),
    ("My landlord sent the Nebenkostenabrechnung two years late", "utility_bill"),
    ("My lease is befristet, can I still leave early?", "fixed_term_lease"),
    ("My landlord wants to kick me out because of Eigenbedarf", "landlord_termination"),
    ("I worked a 12 hour shift without a break", "working_hours"),
    ("Do I pay social insurance for my summer holiday job?", "short_term_job"),
    ("My Minijob colleague in full-time gets more per hour for the same job", "equal_pay_parttime"),
    ("They asked me in the job interview if I am pregnant", "interview_questions"),
    ("Can I get Wohngeld as a student?", "wohngeld"),
    ("The bank refused to open an account for me", "basic_account"),
    ("My phone contract with Vodafone runs 24 months, when can I cancel?", "phone_contract"),
    ("How do I cancel a streaming subscription online?", "cancel_button"),
    ("A company sent me a package I didn't order and now wants money", "unordered_goods"),
    ("Which questions can a landlord ask in a flat application?", "tenant_selfdisclosure"),
    ("How long can I stay in Germany to find a job after my master's?", "job_search_after_degree"),
    ("How much money do I need in a Sperrkonto for the student visa?", "blocked_account_amount"),
    ("My residence permit expires but the Ausländerbehörde has not answered my extension", "residence_permit_extension"),
    ("My boss never gave me a written contract", "written_contract_terms"),
    ("My befristet contract was signed after I started working", "fixed_term_needs_writing"),
    ("I got fired, how long do I have to go to the Arbeitsgericht?", "dismissal_three_weeks"),
    ("Do I get paid for Easter Monday in my Minijob?", "holiday_pay"),
    ("When do I need a Krankschreibung for my employer?", "sick_notification"),
    ("My manager keeps part of the tips in the restaurant", "tips_belong_to_you"),
    ("My contract says overtime is already included in my salary", "overtime_flat_clause"),
    ("Why is 3.6 percent pension taken from my Minijob pay?", "minijob_pension"),
    ("I think I was rejected for a job because of my headscarf", "discriminated_application"),
    ("How much BAföG do I have to pay back after my degree?", "bafoeg_repayment"),
    ("I want to switch my degree in the 5th semester, do I keep BAföG?", "bafoeg_change_subject"),
    ("I am late with my BAföG application, do I lose money?", "bafoeg_apply_early"),
    ("How much can I earn next to BAföG with a student job?", "bafoeg_side_job"),
    ("Do my parents lose Kindergeld if I earn too much in my second degree?", "kindergeld_side_job"),
    ("Until what income can I stay in my parents' Familienversicherung?", "family_insurance_limit"),
    ("What do I pay in social insurance as a Werkstudent?", "werkstudent_contributions"),
    ("I am two months behind with rent, can my landlord throw me out?", "rent_arrears_termination"),
    ("My laptop broke after 8 months and the shop refuses a repair", "warranty_twelve_months"),
    ("My flight was delayed by four hours, do I get compensation?", "flight_delay_compensation"),
    ("Do I get holiday in my voluntary internship?", "internship_holiday"),
    ("My boss fired me on the spot without notice", "termination_without_notice"),
    ("I forgot to pay my semester fee on time, will I be exmatriculated?", "semester_fee_deadline"),
    ("How much does the Deutschland-Semesterticket cost per semester?", "semester_ticket_price"),
    ("I only applied for Kindergeld now, can I get it for last year?", "kindergeld_six_months"),
    ("Do my parents get Kindergeld in the months between school and my first semester?", "kindergeld_gap_months"),
    ("I failed my exam for the third time, am I thrown out of university?", "exam_final_fail"),
    ("Does my student health insurance end after the 14th semester?", "student_insurance_no_semester_limit"),
    ("How do I get overpaid rent back after a Mietpreisbremse violation?", "rent_brake_complaint"),
    ("Can I send back custom made goods I bought online within 14 days?", "withdrawal_exceptions"),
    ("My flatmate gets BAföG and is exempt from Rundfunkbeitrag, do I still have to pay?", "broadcast_fee_wg"),
    ("I get BAföG only as a loan, can I apply for Wohngeld?", "wohngeld_exceptions"),
    ("As a non-EU student can I work 20 hours a week during lectures?", "intl_work_20h"),
    ("Does my compulsory internship count towards the 140 days for international students?", "intl_compulsory_internship"),
    ("What is the Grundfreibetrag in 2026 and do I have to file a tax return?", "tax_allowance_2026"),
    ("Do I have to pay Zweitwohnungsteuer in Munich as a student?", "second_home_tax_munich"),
    ("How much is the KfW Studienkredit interest and how much can I borrow a month?", "kfw_study_loan"),
    ("Do I still get BAföG in my Urlaubssemester?", "leave_semester_bafoeg"),
    ("Am I allowed to write exams while I am beurlaubt?", "leave_semester_exams"),
    ("What happens if I get caught cheating or plagiarising in my thesis?", "cheating_plagiarism"),
    ("Can I ask for extra writing time after I already failed the exam?", "nachteilsausgleich_deadline"),
    ("My fixed-term contract has a probation as long as the whole contract, what notice applies?", "probation_fixed_term"),
    ("Can my employer send my job reference by email and can I get a Zwischenzeugnis?", "reference_details"),
    ("My employer won't pay my overtime, how do I prove the hours?", "overtime_proof"),
    ("I have a baby, do I get an extra child care supplement with BAföG?", "student_parent_bafoeg"),
    ("My mobile provider raised the price, can I cancel early?", "mobile_price_increase"),
    ("How do I get my Schufa report for free?", "schufa_free_copy"),
    ("Can I get BAföG for one more semester after the standard period?", "bafoeg_flexi_semester"),
    ("Do I need a Leistungsnachweis for BAföG after the 4th semester?", "bafoeg_performance_proof"),
    ("Do I get BAföG for a semester abroad with Erasmus?", "bafoeg_abroad"),
    ("Am I still covered by my parents' Haftpflichtversicherung as a student?", "liability_insurance_student"),
    ("I am privately insured, can I switch to the statutory student insurance later?", "health_insurance_exemption"),
    ("My landlord gave notice because of Eigenbedarf, can I object?", "eigenbedarf_hardship_objection"),
    ("My lease has a Staffelmiete, is that allowed?", "rent_step_index"),
    ("My electricity provider raised the price, can I cancel at once?", "energy_price_exit"),
    ("Can I use photos from Google in my presentation or post them online?", "copyright_images_papers"),
    ("How long can a gym contract run and can I cancel monthly?", "gym_contract"),
    ("Can I get my Semesterticket money back?", "semesterticket_refund"),
    ("Until when do I have to cancel my Deutschlandticket subscription?", "deutschlandticket_cancel"),
    ("Do I get minimum wage if I write my thesis at a company?", "thesis_in_company"),
    ("I cannot finish my Bachelorarbeit in time, can I get an extension?", "thesis_deadline_extension"),
    ("Is attendance in lectures compulsory?", "attendance_obligation"),
    ("Can I apply for a Master's before my Bachelor is finished?", "master_provisional_admission"),
    ("My flatmate moved out and does not pay rent, am I liable for the whole rent?", "wg_joint_liability"),
    ("Can my landlord forbid me to keep a cat?", "pets_in_flat"),
    ("Someone emptied my bank account through phishing, will the bank refund me?", "phishing_bank_refund"),
    ("If I quit my job myself, will I get a Sperrzeit for Arbeitslosengeld?", "quit_unemployment_block"),
    ("Does my unused holiday expire at the end of the year?", "vacation_expiry"),
    ("Do I get extra pay for working on Sundays and public holidays?", "sunday_holiday_pay"),
    ("My train was 90 minutes late, how much money do I get back?", "rail_delay_compensation"),
    ("The phone I bought on Kleinanzeigen is broken, can I get my money back from the private seller?", "private_sale_warranty"),
    ("I am moving flat, what happens to my internet contract?", "internet_move_cancel"),
    ("My boss fired me after 4 months in a small firm with 6 employees, is that allowed?", "small_business_dismissal"),
    ("I am pregnant, what are my rights as a student at university?", "maternity_protection_students"),
    ("I had an accident on my way to the university, is it covered by accident insurance?", "student_accident_insurance"),
    ("Do I need permission from my employer to take a second job?", "side_job_approval"),
    ("A restaurant wants me to do an unpaid trial day, is that legal?", "trial_work_unpaid"),
    ("Can I retake an exam I passed to improve my grade?", "exam_grade_improvement"),
    ("How do I get my courses recognised after switching university?", "credit_recognition"),
    ("Does my landlord have to keep my deposit in a separate account with interest?", "deposit_separate_account"),
    ("What are the quiet hours in my flat, can I have a party?", "quiet_hours"),
    ("My bike was stolen on the street, does my home contents insurance pay?", "bike_theft_insurance"),
    ("I forgot my Deutschlandticket and got a 60 euro fine in the train", "fare_dodging_fee"),
    ("My bank terminated my current account, what notice period applies?", "bank_account_termination"),
    ("I moved out and the landlord wants money for damage, we did a handover protocol", "handover_protocol"),
    ("Who has to check the smoke detectors in my Munich flat?", "smoke_detectors_bavaria"),
    ("My heating costs are not billed by consumption, can I cut 15 percent?", "heating_cost_cut"),
    ("Do I get BAföG for a second degree?", "second_degree_bafoeg"),
    ("When am I exmatriculated automatically, and can I apply for exmatriculation myself?", "forced_exmatriculation"),
    ("Can I study part-time and still get BAföG?", "part_time_study"),
    ("My residence permit expired but I applied for the extension, can I keep working?", "fiktionsbescheinigung"),
    ("My employer wants me to repay the training costs after I quit", "training_cost_repayment"),
    ("Do working students get a work reference when the job ends?", "work_reference_right"),
    ("Who pays the return postage for an online order?", "online_return_costs"),
    ("Netflix raised its price, is that allowed without my consent?", "streaming_price_increase"),
    ("My credit card was stolen, how much do I have to pay?", "card_loss_liability"),
    ("Can I leave my lease early if I find three replacement tenants?", "nachmieter_no_right"),
    ("There is mold on my bedroom wall, what should I do as a tenant?", "mold_report_landlord"),
    ("Can my landlord charge me for the janitor's emergency service fee in the utility bill?", "betriebskosten_catalog"),
    ("Does my student dorm contract end automatically on a fixed date?", "dorm_contract"),
    ("How many vacation days do I get if I work three days a week as a Werkstudent?", "vacation_by_days"),
    ("My employer wants me to sign an Aufhebungsvertrag, will I lose unemployment benefit?", "aufhebungsvertrag"),
    ("My employer has not paid my salary, how long can I claim it?", "unpaid_wages_claim"),
    ("Can my employer call me in for a shift on short notice with on-call work?", "on_call_work"),
    ("Am I allowed to use ChatGPT for my Hausarbeit?", "ai_in_exams"),
    ("Do I get a certificate after my internship?", "internship_contract_proof"),
    ("Does my German health insurance cover me during Erasmus with the EHIC?", "study_abroad_health"),
    ("How fast can I end the sublease for a furnished room in my flat?", "sublet_furnished_notice"),
])
def test_finds_the_right_rule(question, expected):
    assert INDEX.search(question)[0] == expected


def test_unknown_question_does_not_guess():
    a = answer("What is the best pizza in Munich?", INDEX)
    assert not a["found"] and a["rules"] == [] and a["free_help"]


def test_answers_only_contain_verified_rules():
    a = answer("deposit too high and landlord enters my room", INDEX)
    assert a["found"]
    for r in a["rules"]:
        assert r["id"] in KB["rules"] and r["summary"] == KB["rules"][r["id"]]["summary"]


def test_every_rule_is_complete():
    for rid, r in KB["rules"].items():
        assert r["area"] in KB["areas"], rid
        assert r["source"].startswith("https://"), rid
        assert r["keywords"], rid
        assert r["area"] in KB["free_help"], rid


def test_deposit_return_question():
    assert INDEX.search("my landlord kept my deposit after I moved out")[0] == "deposit_return"
