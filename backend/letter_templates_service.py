"""
Сервис для работы с шаблонами писем и генерации официальных документов
"""
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class LetterTemplatesService:
    def __init__(self):
        self.templates = self._load_german_letter_templates()
    
    def _load_german_letter_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов немецких официальных писем"""
        return {
            "job_center": {
                "name": "Jobcenter / Arbeitsagentur",
                "icon": "🏢",
                "templates": {
                    "widerspruch_sanktion": {
                        "name": "Widerspruch gegen Sanktion",
                        "description": "Возражение против санкций",
                        "template": """Widerspruch gegen den Bescheid vom {date}

Sehr geehrte Damen und Herren,

hiermit lege ich Widerspruch gegen Ihren Bescheid vom {date}, Aktenzeichen {aktenzeichen}, ein.

{custom_reason}

Begründung:
{detailed_reasoning}

Ich bitte Sie, den angefochtenen Bescheid aufzuheben und {requested_outcome}.

Mit freundlichen Grüßen
{sender_name}"""
                    },
                    "antrag_mehrbedarf": {
                        "name": "Antrag auf Mehrbedarf",
                        "description": "Заявление на дополнительные потребности",
                        "template": """Antrag auf Mehrbedarf

Sehr geehrte Damen und Herren,

hiermit beantrage ich die Gewährung von Mehrbedarf gemäß § 21 SGB II für {mehrbedarf_type}.

Begründung:
{reason_for_mehrbedarf}

Folgende Nachweise füge ich bei:
{attached_documents}

Ich bitte Sie, meinem Antrag stattzugeben.

Mit freundlichen Grüßen
{sender_name}"""
                    },
                    "erstantrag_alg2": {
                        "name": "Erstantrag ALG II",
                        "description": "Первичное заявление на ALG II",
                        "template": """Antrag auf Leistungen nach dem SGB II (Arbeitslosengeld II)

Sehr geehrte Damen und Herren,

hiermit beantrage ich Leistungen nach dem Sozialgesetzbuch II (Arbeitslosengeld II) ab dem {start_date}.

Persönliche Daten:
{personal_data}

Haushaltsgemeinschaft:
{household_info}

Begründung der Hilfebedürftigkeit:
{reason_for_support}

Ich versichere, dass alle Angaben wahrheitsgemäß und vollständig sind.

Mit freundlichen Grüßen
{sender_name}"""
                    }
                }
            },
            "bamf": {
                "name": "BAMF (Bundesamt für Migration)",
                "icon": "🏛️",
                "templates": {
                    "asylantrag_nachfrage": {
                        "name": "Nachfrage zum Asylverfahren",
                        "description": "Запрос о ходе процедуры предоставления убежища",
                        "template": """Anfrage zum Stand des Asylverfahrens

Sehr geehrte Damen und Herren,

hiermit erkundige ich mich nach dem aktuellen Stand meines Asylverfahrens.

Aktenzeichen: {aktenzeichen}
Antragsdatum: {application_date}

{specific_question}

Ich bitte um eine zeitnahe Rückmeldung zum Bearbeitungsstand.

Mit freundlichen Grüßen
{sender_name}"""
                    },
                    "familiennachzug": {
                        "name": "Antrag Familiennachzug",
                        "description": "Заявление на воссоединение семьи",
                        "template": """Antrag auf Familiennachzug

Sehr geehrte Damen und Herren,

hiermit beantrage ich den Nachzug meiner Familie nach Deutschland.

Angaben zur Person:
{applicant_info}

Angaben zu nachzuziehenden Familienangehörigen:
{family_members}

Begründung:
{justification}

Folgende Unterlagen füge ich bei:
{documents_list}

Mit freundlichen Grüßen
{sender_name}"""
                    },
                    "aufenthaltstitel_verlaengerung": {
                        "name": "Verlängerung Aufenthaltstitel",
                        "description": "Продление вида на жительство",
                        "template": """Antrag auf Verlängerung des Aufenthaltstitels

Sehr geehrte Damen und Herren,

hiermit beantrage ich die Verlängerung meines Aufenthaltstitels.

Aktuelle Aufenthaltserlaubnis:
Gültig bis: {current_expiry}
Paragraph: {current_paragraph}

Begründung für die Verlängerung:
{extension_reason}

Aktuelle Situation:
{current_situation}

Ich bitte um zeitnahe Bearbeitung meines Antrags.

Mit freundlichen Grüßen
{sender_name}"""
                    }
                }
            },
            "medical": {
                "name": "Medizinische Einrichtungen",
                "icon": "🏥",
                "templates": {
                    "arzttermin_absage": {
                        "name": "Arzttermin absagen",
                        "description": "Отмена врачебного приема",
                        "template": """Absage des Termins am {appointment_date}

Sehr geehrte Damen und Herren,

leider muss ich meinen Termin am {appointment_date} um {appointment_time} Uhr absagen.

Grund der Absage:
{cancellation_reason}

Ich bitte um einen neuen Termin. {preferred_dates}

Mit freundlichen Grüßen
{sender_name}"""
                    },
                    "krankschreibung_verlaengerung": {
                        "name": "Verlängerung Krankschreibung",
                        "description": "Продление больничного листа",
                        "template": """Bitte um Verlängerung der Arbeitsunfähigkeitsbescheinigung

Sehr geehrte/r Dr. {doctor_name},

hiermit bitte ich um eine Verlängerung meiner Arbeitsunfähigkeitsbescheinigung.

Aktuelle AU bis: {current_sick_leave_end}
Grund: {illness_reason}

Begründung für die Verlängerung:
{extension_justification}

Ich bitte um einen zeitnahen Termin zur Untersuchung.

Mit freundlichen Grüßen
{sender_name}"""
                    },
                    "kostenuebernehmeantrag": {
                        "name": "Kostenübernahmeantrag",
                        "description": "Заявление на покрытие расходов",
                        "template": """Antrag auf Kostenübernahme

Sehr geehrte Damen und Herren,

hiermit beantrage ich die Übernahme der Kosten für {treatment_type}.

Behandlung/Therapie: {treatment_details}
Voraussichtliche Kosten: {estimated_costs}

Medizinische Begründung:
{medical_justification}

Folgende Unterlagen füge ich bei:
{attached_medical_documents}

Mit freundlichen Grüßen
{sender_name}"""
                    }
                }
            },
            "school": {
                "name": "Schulen & Bildung",
                "icon": "🎓",
                "templates": {
                    "krankmeldung_kind": {
                        "name": "Krankmeldung für Kind",
                        "description": "Уведомление о болезни ребенка",
                        "template": """Krankmeldung für {child_name}

Sehr geehrte Damen und Herren,

hiermit teile ich mit, dass mein Kind {child_name}, Klasse {class_name}, vom {start_date} bis voraussichtlich {end_date} krankheitsbedingt nicht am Unterricht teilnehmen kann.

Grund: {illness_reason}

{additional_info}

Eine ärztliche Bescheinigung {medical_certificate_info}.

Mit freundlichen Grüßen
{parent_name}"""
                    },
                    "beurlaubung_antrag": {
                        "name": "Beurlaubungsantrag",
                        "description": "Заявление на освобождение от занятий",
                        "template": """Antrag auf Beurlaubung

Sehr geehrte Damen und Herren,

hiermit beantrage ich für mein Kind {child_name}, Klasse {class_name}, eine Beurlaubung vom Unterricht.

Zeitraum: {absence_period}
Grund der Beurlaubung: {absence_reason}

Begründung:
{detailed_justification}

Ich versichere, dass der versäumte Unterrichtsstoff eigenverantwortlich nachgeholt wird.

Mit freundlichen Grüßen
{parent_name}"""
                    },
                    "schulplatz_antrag": {
                        "name": "Schulplatzantrag",
                        "description": "Заявление на место в школе",
                        "template": """Antrag auf Schulplatz

Sehr geehrte Schulleitung,

hiermit beantrage ich für mein Kind {child_name}, geboren am {child_birthdate}, einen Schulplatz an Ihrer Schule.

Gewünschter Einschulungstermin: {desired_start_date}
Gewünschte Klassenstufe: {desired_grade}

Angaben zum Kind:
{child_information}

Besondere Bedürfnisse/Förderung:
{special_needs}

Ich würde mich über ein persönliches Gespräch freuen.

Mit freundlichen Grüßen
{parent_name}"""
                    }
                }
            },
            "employment": {
                "name": "Arbeitgeber & Bewerbungen",
                "icon": "💼",
                "templates": {
                    "bewerbungsschreiben": {
                        "name": "Bewerbungsschreiben",
                        "description": "Сопроводительное письмо",
                        "template": """Bewerbung um die Stelle als {position}

Sehr geehrte Damen und Herren,

mit großem Interesse habe ich Ihre Stellenausschreibung für die Position als {position} gelesen. Hiermit bewerbe ich mich um diese Stelle.

Über mich:
{personal_introduction}

Meine Qualifikationen:
{qualifications}

Berufserfahrung:
{work_experience}

Warum ich zu Ihrem Unternehmen passe:
{company_fit}

Über eine Einladung zu einem Vorstellungsgespräch würde ich mich sehr freuen.

Mit freundlichen Grüßen
{sender_name}"""
                    },
                    "kuendigung": {
                        "name": "Kündigung",
                        "description": "Уведомление об увольнении",
                        "template": """Kündigung des Arbeitsvertrags

Sehr geehrte/r {employer_name},

hiermit kündige ich meinen Arbeitsvertrag, geschlossen am {contract_date}, ordentlich zum {termination_date}.

{termination_reason}

Ich bitte um eine schriftliche Bestätigung der Kündigung sowie um ein qualifiziertes Arbeitszeugnis.

Die ordnungsgemäße Übergabe meiner Aufgaben werde ich gewährleisten.

Mit freundlichen Grüßen
{sender_name}"""
                    },
                    "gehaltsverhandlung": {
                        "name": "Gehaltsverhandlung",
                        "description": "Переговоры о зарплате",
                        "template": """Bitte um Gehaltsgespräch

Sehr geehrte/r {supervisor_name},

hiermit bitte ich Sie um ein Gespräch bezüglich einer Anpassung meiner Vergütung.

Aktuelle Position: {current_position}
Beschäftigungsdauer: {employment_duration}

Begründung für die Gehaltsanpassung:
{salary_justification}

Erreichte Erfolge/Leistungen:
{achievements}

Ich würde mich über einen Gesprächstermin freuen.

Mit freundlichen Grüßen
{sender_name}"""
                    }
                }
            },
            "housing": {
                "name": "Wohnen & Vermieter",
                "icon": "🏠",
                "templates": {
                    "mietminderung": {
                        "name": "Mietminderung",
                        "description": "Снижение арендной платы",
                        "template": """Anzeige von Wohnungsmängeln und Mietminderung

Sehr geehrte/r {landlord_name},

hiermit zeige ich Ihnen Mängel in der Wohnung {apartment_address} an und mindere die Miete entsprechend.

Festgestellte Mängel:
{defects_list}

Zeitpunkt der Feststellung: {discovery_date}

Die Mängel führen zu einer Gebrauchsbeeinträchtigung von ca. {percentage}%, daher mindere ich die Miete um {reduction_amount} Euro ab {reduction_start_date}.

Ich bitte um umgehende Mängelbeseitigung.

Mit freundlichen Grüßen
{tenant_name}"""
                    },
                    "kuendigung_mietvertrag": {
                        "name": "Kündigung Mietvertrag",
                        "description": "Расторжение договора аренды",
                        "template": """Kündigung des Mietvertrags

Sehr geehrte/r {landlord_name},

hiermit kündige ich den Mietvertrag für die Wohnung {apartment_address}, Mietbeginn {rental_start_date}, ordentlich zum {termination_date}.

{termination_reason}

Die Wohnung wird ordnungsgemäß übergeben. Ich bitte um einen Übergabetermin.

Meine neue Anschrift ab {move_date}: {new_address}

Mit freundlichen Grüßen
{tenant_name}"""
                    },
                    "nebenkostenabrechnung_einspruch": {
                        "name": "Einspruch Nebenkostenabrechnung",
                        "description": "Возражение против счета за дополнительные расходы",
                        "template": """Einspruch gegen Nebenkostenabrechnung

Sehr geehrte/r {landlord_name},

gegen Ihre Nebenkostenabrechnung für den Zeitraum {billing_period} lege ich hiermit Einspruch ein.

Beanstandete Punkte:
{objections_list}

Begründung:
{detailed_objections}

Ich bitte um Korrektur der Abrechnung und Übersendung der entsprechenden Belege.

Mit freundlichen Grüßen
{tenant_name}"""
                    }
                }
            },
            "insurance": {
                "name": "Versicherungen",
                "icon": "🛡️",
                "templates": {
                    "schadensmeldung": {
                        "name": "Schadensmeldung",
                        "description": "Заявление о страховом случае",
                        "template": """Schadensmeldung

Sehr geehrte Damen und Herren,

hiermit melde ich einen Schaden zur Regulierung an.

Versicherungsnummer: {policy_number}
Schadendatum: {damage_date}
Schadenort: {damage_location}

Schadenshergang:
{damage_description}

Schadenshöhe (geschätzt): {estimated_damage}

Folgende Unterlagen füge ich bei:
{attached_documents}

Ich bitte um zeitnahe Bearbeitung.

Mit freundlichen Grüßen
{sender_name}"""
                    },
                    "versicherung_kuendigung": {
                        "name": "Versicherung kündigen",
                        "description": "Расторжение страхового договора",
                        "template": """Kündigung der Versicherung

Sehr geehrte Damen und Herren,

hiermit kündige ich meine Versicherung mit der Versicherungsnummer {policy_number} zum {termination_date}.

{cancellation_reason}

Ich bitte um schriftliche Bestätigung der Kündigung.

Mit freundlichen Grüßen
{sender_name}"""
                    }
                }
            },
            "legal": {
                "name": "Rechtliche Angelegenheiten",
                "icon": "⚖️",
                "templates": {
                    "vollmacht": {
                        "name": "Vollmacht",
                        "description": "Доверенность",
                        "template": """Vollmacht

Ich, {authorizer_name}, geboren am {authorizer_birthdate}, wohnhaft {authorizer_address}, erteile hiermit

Herrn/Frau {authorized_person_name}, geboren am {authorized_birthdate}, wohnhaft {authorized_address},

Vollmacht zur {authorization_scope}.

Diese Vollmacht umfasst:
{powers_list}

Die Vollmacht ist {validity_period}.

{additional_conditions}

Ort, Datum: {place_date}
Unterschrift: _________________
{authorizer_name}"""
                    },
                    "widerspruch_bescheid": {
                        "name": "Widerspruch gegen Bescheid",
                        "description": "Возражение против постановления",
                        "template": """Widerspruch

Sehr geehrte Damen und Herren,

gegen Ihren Bescheid vom {decision_date}, eingegangen am {received_date}, Aktenzeichen {case_number}, lege ich hiermit form- und fristgerecht Widerspruch ein.

Begründung:
{objection_reasons}

Ich beantrage, den angefochtenen Bescheid aufzuheben und {desired_outcome}.

Zur Begründung führe ich aus:
{detailed_reasoning}

Mit freundlichen Grüßen
{sender_name}"""
                    }
                }
            }
        }

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Получить все категории шаблонов"""
        categories = []
        for key, category in self.templates.items():
            categories.append({
                "key": key,
                "name": category["name"],
                "icon": category["icon"],
                "template_count": len(category["templates"])
            })
        return categories

    def get_templates_by_category(self, category_key: str) -> List[Dict[str, Any]]:
        """Получить все шаблоны в категории"""
        if category_key not in self.templates:
            return []
        
        category = self.templates[category_key]
        templates = []
        
        for template_key, template_data in category["templates"].items():
            templates.append({
                "key": template_key,
                "name": template_data["name"],
                "description": template_data["description"],
                "category": category_key
            })
        
        return templates

    def get_template(self, category_key: str, template_key: str) -> Optional[Dict[str, Any]]:
        """Получить конкретный шаблон"""
        if category_key not in self.templates:
            return None
        
        category = self.templates[category_key]
        if template_key not in category["templates"]:
            return None
        
        template = category["templates"][template_key]
        return {
            "key": template_key,
            "category": category_key,
            "name": template["name"],
            "description": template["description"],
            "template": template["template"],
            "variables": self._extract_variables(template["template"])
        }

    def _extract_variables(self, template: str) -> List[str]:
        """Извлечь переменные из шаблона"""
        import re
        variables = re.findall(r'\{([^}]+)\}', template)
        return list(set(variables))  # Уникальные переменные

    def get_all_templates_search(self, query: str) -> List[Dict[str, Any]]:
        """Поиск шаблонов по запросу"""
        query = query.lower()
        results = []
        
        for category_key, category in self.templates.items():
            for template_key, template_data in category["templates"].items():
                if (query in template_data["name"].lower() or 
                    query in template_data["description"].lower()):
                    results.append({
                        "key": template_key,
                        "category": category_key,
                        "name": template_data["name"],
                        "description": template_data["description"],
                        "category_name": category["name"],
                        "category_icon": category["icon"]
                    })
        
        return results

# Глобальный экземпляр сервиса
letter_templates_service = LetterTemplatesService()