"""
BDD Generator Module
Generates Behavior Driven Development scenarios from AI analysis
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger
import yaml
from datetime import datetime
import os


@dataclass
class BDDScenario:
    """BDD Scenario structure"""
    feature: str
    scenario: str
    given: List[str]
    when: List[str]
    then: List[str]
    tags: List[str]
    priority: str
    test_type: str


@dataclass
class BDDFeature:
    """BDD Feature structure"""
    name: str
    description: str
    scenarios: List[BDDScenario]
    background: Optional[str] = None
    tags: List[str] = None


class BDDGenerator:
    """Generator for BDD scenarios from AI analysis"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.language = self.config['bdd']['language']
        self.scenario_count = self.config['bdd']['scenario_count']
        self.include_negative = self.config['bdd']['include_negative_tests']
        self.include_performance = self.config['bdd']['include_performance_tests']
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise
    
    def generate_bdd_from_analysis(self, analysis_data: Dict, ai_scenarios: str) -> List[BDDFeature]:
        """Generate BDD features from AI analysis and scenarios"""
        logger.info("Generating BDD scenarios from AI analysis")
        
        # Parse AI generated scenarios
        parsed_scenarios = self._parse_ai_scenarios(ai_scenarios)
        
        # Generate additional scenarios based on analysis
        generated_scenarios = self._generate_scenarios_from_analysis(analysis_data)
        
        # Combine and organize scenarios
        all_scenarios = parsed_scenarios + generated_scenarios
        
        # Group scenarios by feature
        features = self._group_scenarios_by_feature(all_scenarios)
        
        logger.info(f"Generated {len(features)} BDD features with {sum(len(f.scenarios) for f in features)} scenarios")
        
        return features
    
    def _parse_ai_scenarios(self, ai_scenarios: str) -> List[BDDScenario]:
        """Parse AI generated scenarios"""
        scenarios = []
        
        # Split by feature/scenario blocks
        blocks = re.split(r'(?:Özellik|Feature):\s*', ai_scenarios)
        
        for block in blocks[1:]:  # Skip first empty block
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            feature_name = lines[0].strip()
            
            # Extract scenarios from this feature
            scenario_blocks = re.split(r'(?:Senaryo|Scenario):\s*', '\n'.join(lines[1:]))
            
            for scenario_block in scenario_blocks[1:]:  # Skip first empty block
                if not scenario_block.strip():
                    continue
                    
                scenario = self._parse_scenario_block(scenario_block, feature_name)
                if scenario:
                    scenarios.append(scenario)
        
        return scenarios
    
    def _parse_scenario_block(self, block: str, feature_name: str) -> Optional[BDDScenario]:
        """Parse individual scenario block"""
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        scenario_name = lines[0]
        given_steps = []
        when_steps = []
        then_steps = []
        current_type = None
        
        for line in lines[1:]:
            line = line.strip()
            
            # Turkish keywords
            if line.startswith(('Diyelim ki', 'Given')):
                current_type = 'given'
                given_steps.append(line.replace('Diyelim ki', '').replace('Given', '').strip())
            elif line.startswith(('Ve', 'And')) and current_type == 'given':
                given_steps.append(line.replace('Ve', '').replace('And', '').strip())
            elif line.startswith(('Eğer', 'When')):
                current_type = 'when'
                when_steps.append(line.replace('Eğer', '').replace('When', '').strip())
            elif line.startswith(('Ve', 'And')) and current_type == 'when':
                when_steps.append(line.replace('Ve', '').replace('And', '').strip())
            elif line.startswith(('O zaman', 'Then')):
                current_type = 'then'
                then_steps.append(line.replace('O zaman', '').replace('Then', '').strip())
            elif line.startswith(('Ve', 'And')) and current_type == 'then':
                then_steps.append(line.replace('Ve', '').replace('And', '').strip())
        
        return BDDScenario(
            feature=feature_name,
            scenario=scenario_name,
            given=given_steps,
            when=when_steps,
            then=then_steps,
            tags=['@automated'],
            priority='medium',
            test_type='functional'
        )
    
    def _generate_scenarios_from_analysis(self, analysis_data: Dict) -> List[BDDScenario]:
        """Generate additional scenarios from page analysis"""
        scenarios = []
        
        # Generate form scenarios
        if 'forms' in analysis_data:
            form_scenarios = self._generate_form_scenarios(analysis_data['forms'])
            scenarios.extend(form_scenarios)
        
        # Generate navigation scenarios
        if 'links' in analysis_data:
            nav_scenarios = self._generate_navigation_scenarios(analysis_data['links'])
            scenarios.extend(nav_scenarios)
        
        # Generate button scenarios
        if 'buttons' in analysis_data:
            button_scenarios = self._generate_button_scenarios(analysis_data['buttons'])
            scenarios.extend(button_scenarios)
        
        return scenarios
    
    def _generate_form_scenarios(self, forms: List[Dict]) -> List[BDDScenario]:
        """Generate scenarios for form testing"""
        scenarios = []
        
        for form in forms:
            if not form.get('fields'):
                continue
                
            form_name = form.get('id', f"form_{len(scenarios)}")
            
            # Positive form submission scenario
            scenarios.append(BDDScenario(
                feature="Form İşlemleri",
                scenario=f"{form_name} formunu başarıyla doldur ve gönder",
                given=[f"Kullanıcı {form_name} formunu içeren sayfadadır"],
                when=[
                    "Kullanıcı tüm zorunlu alanları geçerli verilerle doldurur",
                    "Kullanıcı gönder butonuna tıklar"
                ],
                then=[
                    "Form başarıyla gönderilir",
                    "Başarı mesajı görüntülenir"
                ],
                tags=['@form', '@positive'],
                priority='high',
                test_type='functional'
            ))
            
            # Negative scenarios for required fields
            required_fields = [f for f in form['fields'] if f.get('required')]
            for field in required_fields:
                scenarios.append(BDDScenario(
                    feature="Form Validasyonu",
                    scenario=f"{field['name']} alanı boş bırakıldığında hata mesajı görüntülenir",
                    given=[f"Kullanıcı {form_name} formunu içeren sayfadadır"],
                    when=[
                        f"Kullanıcı {field['name']} alanını boş bırakır",
                        "Kullanıcı gönder butonuna tıklar"
                    ],
                    then=[
                        "Form gönderilmez",
                        f"{field['name']} alanı için hata mesajı görüntülenir"
                    ],
                    tags=['@form', '@validation', '@negative'],
                    priority='medium',
                    test_type='validation'
                ))
        
        return scenarios
    
    def _generate_navigation_scenarios(self, links: List[Dict]) -> List[BDDScenario]:
        """Generate scenarios for navigation testing"""
        scenarios = []
        
        # Filter important links (exclude external, empty, and javascript links)
        important_links = [
            link for link in links 
            if link.get('href') and 
            not link.get('is_external', False) and
            not link['href'].startswith(('javascript:', 'mailto:', 'tel:'))
        ]
        
        for link in important_links[:5]:  # Limit to first 5 important links
            scenarios.append(BDDScenario(
                feature="Navigasyon",
                scenario=f"'{link['text']}' linkine tıklama",
                given=["Kullanıcı ana sayfadadır"],
                when=[f"Kullanıcı '{link['text']}' linkine tıklar"],
                then=[
                    "Yeni sayfa yüklenir",
                    "Sayfa başarıyla görüntülenir"
                ],
                tags=['@navigation', '@link'],
                priority='low',
                test_type='functional'
            ))
        
        return scenarios
    
    def _generate_button_scenarios(self, buttons: List[Dict]) -> List[BDDScenario]:
        """Generate scenarios for button testing"""
        scenarios = []
        
        for button in buttons:
            if not button.get('text'):
                continue
                
            button_text = button['text']
            button_type = button.get('type', 'button')
            
            # Skip form submit buttons (already covered in form scenarios)
            if button_type == 'submit':
                continue
            
            scenarios.append(BDDScenario(
                feature="Buton İşlemleri",
                scenario=f"'{button_text}' butonuna tıklama",
                given=["Kullanıcı sayfadadır"],
                when=[f"Kullanıcı '{button_text}' butonuna tıklar"],
                then=[
                    "Buton tıklaması gerçekleşir",
                    "Beklenen işlem yapılır"
                ],
                tags=['@button', '@interaction'],
                priority='medium',
                test_type='functional'
            ))
        
        return scenarios
    
    def _group_scenarios_by_feature(self, scenarios: List[BDDScenario]) -> List[BDDFeature]:
        """Group scenarios by feature"""
        features_dict = {}
        
        for scenario in scenarios:
            feature_name = scenario.feature
            
            if feature_name not in features_dict:
                features_dict[feature_name] = BDDFeature(
                    name=feature_name,
                    description=f"{feature_name} ile ilgili test senaryoları",
                    scenarios=[],
                    tags=['@automated']
                )
            
            features_dict[feature_name].scenarios.append(scenario)
        
        return list(features_dict.values())
    
    def generate_feature_file(self, feature: BDDFeature, output_dir: str = "tests/features") -> str:
        """Generate Gherkin feature file"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Clean feature name for filename
        filename = re.sub(r'[^\w\s-]', '', feature.name.lower())
        filename = re.sub(r'[-\s]+', '-', filename)
        filepath = os.path.join(output_dir, f"{filename}.feature")
        
        content = self._generate_feature_content(feature)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Feature file generated: {filepath}")
        return filepath
    
    def _generate_feature_content(self, feature: BDDFeature) -> str:
        """Generate Gherkin feature file content"""
        content = []
        
        # Feature header
        if feature.tags:
            content.append(' '.join(feature.tags))
        
        content.append(f"Özellik: {feature.name}")
        content.append(f"  {feature.description}")
        content.append("")
        
        # Background if exists
        if feature.background:
            content.append("  Arka Plan:")
            content.append(f"    {feature.background}")
            content.append("")
        
        # Scenarios
        for scenario in feature.scenarios:
            # Tags
            if scenario.tags:
                content.append(f"  {' '.join(scenario.tags)}")
            
            # Scenario header
            content.append(f"  Senaryo: {scenario.scenario}")
            
            # Given steps
            for i, step in enumerate(scenario.given):
                prefix = "    Diyelim ki" if i == 0 else "    Ve"
                content.append(f"{prefix} {step}")
            
            # When steps
            for i, step in enumerate(scenario.when):
                prefix = "    Eğer" if i == 0 else "    Ve"
                content.append(f"{prefix} {step}")
            
            # Then steps
            for i, step in enumerate(scenario.then):
                prefix = "    O zaman" if i == 0 else "    Ve"
                content.append(f"{prefix} {step}")
            
            content.append("")
        
        return '\n'.join(content)
    
    def generate_all_feature_files(self, features: List[BDDFeature], output_dir: str = "tests/features") -> List[str]:
        """Generate all feature files"""
        filepaths = []
        
        for feature in features:
            filepath = self.generate_feature_file(feature, output_dir)
            filepaths.append(filepath)
        
        return filepaths
    
    def generate_scenario_summary(self, features: List[BDDFeature]) -> Dict:
        """Generate summary of all scenarios"""
        summary = {
            'total_features': len(features),
            'total_scenarios': sum(len(f.scenarios) for f in features),
            'by_priority': {'high': 0, 'medium': 0, 'low': 0},
            'by_type': {},
            'by_tags': {},
            'features': []
        }
        
        for feature in features:
            feature_summary = {
                'name': feature.name,
                'scenario_count': len(feature.scenarios),
                'scenarios': []
            }
            
            for scenario in feature.scenarios:
                # Count by priority
                summary['by_priority'][scenario.priority] += 1
                
                # Count by type
                if scenario.test_type in summary['by_type']:
                    summary['by_type'][scenario.test_type] += 1
                else:
                    summary['by_type'][scenario.test_type] = 1
                
                # Count by tags
                for tag in scenario.tags:
                    if tag in summary['by_tags']:
                        summary['by_tags'][tag] += 1
                    else:
                        summary['by_tags'][tag] = 1
                
                feature_summary['scenarios'].append({
                    'name': scenario.scenario,
                    'priority': scenario.priority,
                    'type': scenario.test_type,
                    'tags': scenario.tags
                })
            
            summary['features'].append(feature_summary)
        
        return summary 