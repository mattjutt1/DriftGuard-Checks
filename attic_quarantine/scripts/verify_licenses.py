#!/usr/bin/env python3
"""
Verify Data Licenses and Copyright Compliance
==============================================
This script verifies that all training data sources comply with:
- MIT License (PromptWizard)
- Apache 2.0 License (compatible datasets)
- Public domain or permissive licenses

Ensures we maintain compliance with our proprietary license.

Copyright (c) 2025 Matthew J. Utt
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# License configuration
LICENSE_CONFIG = {
    "compatible_licenses": [
        "MIT",
        "Apache-2.0",
        "Apache 2.0",
        "BSD",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "CC0",
        "CC-BY",
        "CC-BY-SA",
        "Public Domain",
        "Unlicense"
    ],
    "incompatible_licenses": [
        "GPL",
        "GPL-2.0",
        "GPL-3.0",
        "AGPL",
        "LGPL",
        "CC-BY-NC",
        "CC-BY-ND",
        "Proprietary",
        "Commercial"
    ],
    "attribution_required": [
        "MIT",
        "Apache-2.0",
        "BSD",
        "CC-BY",
        "CC-BY-SA"
    ],
    "our_license": "Proprietary - Copyright (c) 2025 Matthew J. Utt"
}

@dataclass
class DataSource:
    """Represents a data source with license information"""
    name: str
    path: Path
    license: Optional[str]
    attribution: Optional[str]
    url: Optional[str]
    verified: bool
    issues: List[str]

@dataclass
class LicenseReport:
    """License verification report"""
    timestamp: str
    total_sources: int
    verified_sources: int
    compatible_sources: int
    incompatible_sources: int
    unknown_sources: int
    issues: List[Dict[str, Any]]
    attributions: List[Dict[str, str]]

class LicenseVerifier:
    """Main class for verifying data licenses"""
    
    def __init__(self):
        self.data_sources = []
        self.attributions = []
        self.issues = []
        self.output_dir = Path(__file__).parent.parent / "licenses"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def scan_data_sources(self) -> List[DataSource]:
        """Scan all data directories for sources"""
        sources = []
        
        # Known source locations
        data_dirs = [
            Path(__file__).parent.parent / "data" / "raw",
            Path(__file__).parent.parent / "data" / "processed",
            Path(__file__).parent.parent / "microsoft-promptwizard"
        ]
        
        for data_dir in data_dirs:
            if not data_dir.exists():
                continue
            
            # Look for data files
            for pattern in ["*.json", "*.jsonl", "*.csv", "*.txt", "*.parquet"]:
                for file_path in data_dir.rglob(pattern):
                    source = self.identify_source(file_path)
                    if source:
                        sources.append(source)
                        logger.info(f"Found source: {source.name} ({source.license})")
        
        # Check PromptWizard specifically
        promptwizard_source = self.verify_promptwizard()
        if promptwizard_source:
            sources.append(promptwizard_source)
        
        self.data_sources = sources
        return sources
    
    def identify_source(self, file_path: Path) -> Optional[DataSource]:
        """Identify and verify a data source"""
        # Skip our generated files
        if any(skip in str(file_path) for skip in ["seed_pairs", "synthesized_pairs", "splits"]):
            return None
        
        # Check for LICENSE file in directory
        license_file = file_path.parent / "LICENSE"
        if not license_file.exists():
            license_file = file_path.parent / "LICENSE.txt"
        if not license_file.exists():
            license_file = file_path.parent / "LICENSE.md"
        
        license_text = None
        if license_file.exists():
            with open(license_file, 'r') as f:
                license_text = f.read()
        
        # Identify license type
        license_type = self.identify_license(license_text) if license_text else None
        
        # Check for attribution requirements
        attribution = None
        if license_type in LICENSE_CONFIG["attribution_required"]:
            attribution = self.extract_attribution(file_path, license_text)
        
        # Create source record
        source = DataSource(
            name=file_path.name,
            path=file_path,
            license=license_type,
            attribution=attribution,
            url=self.extract_url(file_path),
            verified=license_type is not None,
            issues=[]
        )
        
        # Check for issues
        if not license_type:
            source.issues.append("No license found")
        elif license_type in LICENSE_CONFIG["incompatible_licenses"]:
            source.issues.append(f"Incompatible license: {license_type}")
        
        return source
    
    def verify_promptwizard(self) -> Optional[DataSource]:
        """Specifically verify PromptWizard license"""
        promptwizard_dir = Path(__file__).parent.parent / "microsoft-promptwizard"
        
        if not promptwizard_dir.exists():
            logger.warning("PromptWizard directory not found")
            return None
        
        license_file = promptwizard_dir / "LICENSE"
        if not license_file.exists():
            logger.error("PromptWizard LICENSE file not found!")
            return DataSource(
                name="PromptWizard",
                path=promptwizard_dir,
                license=None,
                attribution="Microsoft PromptWizard",
                url="https://github.com/microsoft/PromptWizard",
                verified=False,
                issues=["LICENSE file missing"]
            )
        
        with open(license_file, 'r') as f:
            license_text = f.read()
        
        # Verify it's MIT
        if "MIT License" in license_text or "MIT" in license_text:
            logger.info("✅ PromptWizard MIT License verified")
            return DataSource(
                name="PromptWizard",
                path=promptwizard_dir,
                license="MIT",
                attribution="Copyright (c) 2023 Microsoft",
                url="https://github.com/microsoft/PromptWizard",
                verified=True,
                issues=[]
            )
        else:
            logger.error("PromptWizard license is not MIT!")
            return DataSource(
                name="PromptWizard",
                path=promptwizard_dir,
                license="Unknown",
                attribution="Microsoft PromptWizard",
                url="https://github.com/microsoft/PromptWizard",
                verified=False,
                issues=["License type unknown"]
            )
    
    def identify_license(self, license_text: str) -> Optional[str]:
        """Identify license type from text"""
        license_text_lower = license_text.lower()
        
        # Check for known licenses
        license_patterns = {
            "MIT": r"mit license|permission is hereby granted.*free of charge",
            "Apache-2.0": r"apache license.*version 2\.0|apache-2\.0",
            "BSD-3-Clause": r"bsd 3-clause|redistribution and use in source and binary forms",
            "BSD-2-Clause": r"bsd 2-clause|simplified bsd",
            "GPL-3.0": r"gnu general public license.*version 3|gpl-3\.0",
            "GPL-2.0": r"gnu general public license.*version 2|gpl-2\.0",
            "CC0": r"cc0|creative commons zero|public domain",
            "CC-BY": r"creative commons attribution|cc-by",
            "Unlicense": r"unlicense|public domain"
        }
        
        for license_name, pattern in license_patterns.items():
            if re.search(pattern, license_text_lower):
                return license_name
        
        return None
    
    def extract_attribution(self, file_path: Path, license_text: Optional[str]) -> Optional[str]:
        """Extract attribution information"""
        attribution_parts = []
        
        # Try to extract from license text
        if license_text:
            # Look for copyright line
            copyright_match = re.search(r"Copyright .*? \d{4} (.*?)(?:\n|$)", license_text)
            if copyright_match:
                attribution_parts.append(copyright_match.group(0).strip())
        
        # Try to extract from README
        readme_file = file_path.parent / "README.md"
        if readme_file.exists():
            with open(readme_file, 'r') as f:
                readme_text = f.read()
                # Look for attribution section
                if "Attribution" in readme_text or "Credits" in readme_text:
                    # Extract relevant section
                    lines = readme_text.split('\n')
                    for i, line in enumerate(lines):
                        if "Attribution" in line or "Credits" in line:
                            # Get next few lines
                            for j in range(i+1, min(i+5, len(lines))):
                                if lines[j].strip():
                                    attribution_parts.append(lines[j].strip())
        
        return " | ".join(attribution_parts) if attribution_parts else None
    
    def extract_url(self, file_path: Path) -> Optional[str]:
        """Extract source URL if available"""
        # Check for URL in parent README
        readme_file = file_path.parent / "README.md"
        if readme_file.exists():
            with open(readme_file, 'r') as f:
                readme_text = f.read()
                # Look for GitHub URLs
                url_match = re.search(r"https://github\.com/[^\s]+", readme_text)
                if url_match:
                    return url_match.group(0)
        
        return None
    
    def verify_compatibility(self) -> bool:
        """Verify all sources are compatible"""
        all_compatible = True
        
        for source in self.data_sources:
            if not source.verified:
                logger.warning(f"⚠️ Unverified source: {source.name}")
                all_compatible = False
                self.issues.append({
                    "source": source.name,
                    "issue": "Unverified license",
                    "path": str(source.path)
                })
            
            elif source.license in LICENSE_CONFIG["incompatible_licenses"]:
                logger.error(f"❌ Incompatible license: {source.name} ({source.license})")
                all_compatible = False
                self.issues.append({
                    "source": source.name,
                    "issue": f"Incompatible license: {source.license}",
                    "path": str(source.path)
                })
            
            elif source.license not in LICENSE_CONFIG["compatible_licenses"]:
                logger.warning(f"⚠️ Unknown license: {source.name} ({source.license})")
                self.issues.append({
                    "source": source.name,
                    "issue": f"Unknown license: {source.license}",
                    "path": str(source.path)
                })
        
        return all_compatible
    
    def generate_attributions(self):
        """Generate attribution file"""
        attributions = []
        
        for source in self.data_sources:
            if source.license in LICENSE_CONFIG["attribution_required"] and source.attribution:
                attributions.append({
                    "source": source.name,
                    "license": source.license,
                    "attribution": source.attribution,
                    "url": source.url
                })
        
        self.attributions = attributions
        
        # Write ATTRIBUTIONS.md
        attributions_file = self.output_dir / "ATTRIBUTIONS.md"
        with open(attributions_file, 'w') as f:
            f.write("# Attributions\n\n")
            f.write("This project uses the following open source components:\n\n")
            
            for attr in attributions:
                f.write(f"## {attr['source']}\n")
                f.write(f"- **License**: {attr['license']}\n")
                f.write(f"- **Attribution**: {attr['attribution']}\n")
                if attr['url']:
                    f.write(f"- **URL**: {attr['url']}\n")
                f.write("\n")
            
            f.write("---\n\n")
            f.write("All other components are proprietary:\n")
            f.write(f"- **License**: {LICENSE_CONFIG['our_license']}\n")
        
        logger.info(f"Generated attributions file: {attributions_file}")
    
    def generate_report(self) -> LicenseReport:
        """Generate license verification report"""
        compatible_count = sum(1 for s in self.data_sources 
                              if s.license in LICENSE_CONFIG["compatible_licenses"])
        incompatible_count = sum(1 for s in self.data_sources 
                                if s.license in LICENSE_CONFIG["incompatible_licenses"])
        unknown_count = sum(1 for s in self.data_sources 
                           if s.license and s.license not in LICENSE_CONFIG["compatible_licenses"] 
                           and s.license not in LICENSE_CONFIG["incompatible_licenses"])
        
        report = LicenseReport(
            timestamp=datetime.now().isoformat(),
            total_sources=len(self.data_sources),
            verified_sources=sum(1 for s in self.data_sources if s.verified),
            compatible_sources=compatible_count,
            incompatible_sources=incompatible_count,
            unknown_sources=unknown_count,
            issues=self.issues,
            attributions=self.attributions
        )
        
        return report
    
    def save_report(self, report: LicenseReport):
        """Save license report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        report_file = self.output_dir / f"license_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": report.timestamp,
                "summary": {
                    "total_sources": report.total_sources,
                    "verified": report.verified_sources,
                    "compatible": report.compatible_sources,
                    "incompatible": report.incompatible_sources,
                    "unknown": report.unknown_sources
                },
                "issues": report.issues,
                "attributions": report.attributions,
                "sources": [
                    {
                        "name": s.name,
                        "path": str(s.path),
                        "license": s.license,
                        "verified": s.verified,
                        "issues": s.issues
                    }
                    for s in self.data_sources
                ]
            }, f, indent=2)
        
        logger.info(f"Saved license report: {report_file}")
        
        # Save markdown report
        md_report_file = self.output_dir / f"LICENSE_REPORT_{timestamp}.md"
        with open(md_report_file, 'w') as f:
            f.write("# License Verification Report\n\n")
            f.write(f"Generated: {report.timestamp}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total Sources: {report.total_sources}\n")
            f.write(f"- Verified: {report.verified_sources}\n")
            f.write(f"- Compatible: {report.compatible_sources}\n")
            f.write(f"- Incompatible: {report.incompatible_sources}\n")
            f.write(f"- Unknown: {report.unknown_sources}\n\n")
            
            if report.issues:
                f.write("## Issues\n\n")
                for issue in report.issues:
                    f.write(f"- **{issue['source']}**: {issue['issue']}\n")
                f.write("\n")
            
            f.write("## Sources\n\n")
            for source in self.data_sources:
                status = "✅" if source.verified and source.license in LICENSE_CONFIG["compatible_licenses"] else "❌"
                f.write(f"- {status} **{source.name}**: {source.license or 'No license'}\n")
        
        logger.info(f"Saved markdown report: {md_report_file}")
    
    def create_license_hash_registry(self):
        """Create hash registry of all data files for integrity verification"""
        registry = {
            "created": datetime.now().isoformat(),
            "files": {}
        }
        
        for source in self.data_sources:
            if source.path.is_file():
                with open(source.path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    registry["files"][str(source.path)] = {
                        "hash": file_hash,
                        "license": source.license,
                        "verified": source.verified
                    }
        
        registry_file = self.output_dir / "data_hash_registry.json"
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        logger.info(f"Created hash registry: {registry_file}")
    
    def run(self) -> bool:
        """Main execution method"""
        logger.info("="*80)
        logger.info("LICENSE VERIFICATION SYSTEM")
        logger.info("="*80)
        
        # Scan data sources
        logger.info("\nScanning data sources...")
        self.scan_data_sources()
        
        # Verify compatibility
        logger.info("\nVerifying license compatibility...")
        is_compatible = self.verify_compatibility()
        
        # Generate attributions
        logger.info("\nGenerating attributions...")
        self.generate_attributions()
        
        # Generate report
        logger.info("\nGenerating report...")
        report = self.generate_report()
        self.save_report(report)
        
        # Create hash registry
        logger.info("\nCreating hash registry...")
        self.create_license_hash_registry()
        
        # Summary
        logger.info("\n" + "="*80)
        if is_compatible:
            logger.info("✅ LICENSE VERIFICATION PASSED")
        else:
            logger.error("❌ LICENSE VERIFICATION FAILED")
        logger.info("="*80)
        
        return is_compatible

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify data licenses and compliance")
    parser.add_argument("--strict", action="store_true",
                       help="Fail on any unverified source")
    parser.add_argument("--update-attributions", action="store_true",
                       help="Update ATTRIBUTIONS.md file")
    
    args = parser.parse_args()
    
    # Run verifier
    verifier = LicenseVerifier()
    success = verifier.run()
    
    # Print summary
    print("\n" + "="*80)
    print("LICENSE VERIFICATION SUMMARY")
    print("="*80)
    
    report = verifier.generate_report()
    print(f"Total Sources:    {report.total_sources}")
    print(f"Verified:         {report.verified_sources}")
    print(f"Compatible:       {report.compatible_sources}")
    print(f"Incompatible:     {report.incompatible_sources}")
    print(f"Unknown:          {report.unknown_sources}")
    
    if report.issues:
        print(f"\n⚠️ Issues Found:  {len(report.issues)}")
        for issue in report.issues[:5]:  # Show first 5 issues
            print(f"  - {issue['source']}: {issue['issue']}")
    
    print("="*80)
    
    # Exit code
    if args.strict and report.verified_sources < report.total_sources:
        return 1
    elif report.incompatible_sources > 0:
        return 1
    return 0

if __name__ == "__main__":
    exit(main())