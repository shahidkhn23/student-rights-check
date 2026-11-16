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
