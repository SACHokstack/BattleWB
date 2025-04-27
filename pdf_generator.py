from fpdf import FPDF
import json
import os
import traceback
import urllib.request

class ResumePDF:
    def __init__(self, margin=10):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=margin)
        self.pdf.add_page()
        
        # Set default font (use Helvetica if DejaVu fonts are unavailable)
        self.font_available = False
        font_path = 'static/fonts/DejaVuSansCondensed.ttf'
        bold_font_path = 'static/fonts/DejaVuSansCondensed-Bold.ttf'
        
        if os.path.exists(font_path) and os.path.exists(bold_font_path):
            try:
                self.pdf.add_font('DejaVu', '', font_path, uni=True)
                self.pdf.add_font('DejaVuBold', '', bold_font_path, uni=True)
                self.font_available = True
            except Exception as e:
                print(f"Failed to load DejaVu fonts: {str(e)}")
        
        # Default colors
        self.text_color = (0, 0, 0)  # Black
        self.accent_color = (70, 130, 180)  # Steel Blue
        
    def set_theme(self, text_color=(0, 0, 0), accent_color=(70, 130, 180)):
        """Set color theme for the resume"""
        self.text_color = text_color
        self.accent_color = accent_color
        
    def add_header(self, name, title):
        """Add the resume header with name and professional title"""
        font = 'DejaVuBold' if self.font_available else 'Helvetica'
        self.pdf.set_font(font, '', 24)
        self.pdf.set_text_color(*self.accent_color)
        self.pdf.cell(0, 10, name, ln=True, align='C')
        
        font = 'DejaVu' if self.font_available else 'Helvetica'
        self.pdf.set_font(font, '', 16)
        self.pdf.set_text_color(*self.text_color)
        self.pdf.cell(0, 10, title, ln=True, align='C')
        
        # Add separator line
        self.pdf.line(10, self.pdf.get_y() + 2, self.pdf.w - 10, self.pdf.get_y() + 2)
        self.pdf.ln(5)
        
    def add_contact_info(self, contact):
        """Add contact information"""
        font = 'DejaVu' if self.font_available else 'Helvetica'
        self.pdf.set_font(font, '', 10)
        
        contact_text = ""
        if 'email' in contact:
            contact_text += f"Email: {contact['email']}   "
        if 'phone' in contact:
            contact_text += f"Phone: {contact['phone']}   "
        if 'linkedin' in contact:
            contact_text += f"LinkedIn: {contact['linkedin']}   "
        if 'website' in contact:
            contact_text += f"Website: {contact['website']}"
            
        self.pdf.cell(0, 5, contact_text, ln=True, align='C')
        self.pdf.ln(5)
        
    def add_section_heading(self, title):
        """Add a section heading"""
        font = 'DejaVuBold' if self.font_available else 'Helvetica'
        self.pdf.set_font(font, '', 14)
        self.pdf.set_text_color(*self.accent_color)
        self.pdf.cell(0, 10, title, ln=True)
        self.pdf.set_text_color(*self.text_color)
        self.pdf.line(10, self.pdf.get_y(), 60, self.pdf.get_y())
        self.pdf.ln(3)
        
    def add_summary(self, summary):
        """Add professional summary"""
        self.add_section_heading("Professional Summary")
        font = 'DejaVu' if self.font_available else 'Helvetica'
        self.pdf.set_font(font, '', 11)
        self.pdf.multi_cell(0, 5, str(summary))
        self.pdf.ln(5)
        
    def add_skills(self, skills):
        """Add skills section"""
        if not skills:
            return
            
        self.add_section_heading("Skills")
        font = 'DejaVu' if self.font_available else 'Helvetica'
        self.pdf.set_font(font, '', 11)
        
        if isinstance(skills, list):
            skills_text = ", ".join(str(skill) for skill in skills)
        else:
            skills_text = str(skills)
            
        self.pdf.multi_cell(0, 5, skills_text)
        self.pdf.ln(5)
        
    def add_experience(self, experience):
        """Add work experience section"""
        if not experience:
            return
            
        self.add_section_heading("Work Experience")
        
        if isinstance(experience, list):
            for job in experience:
                if isinstance(job, dict):
                    font = 'DejaVuBold' if self.font_available else 'Helvetica'
                    self.pdf.set_font(font, '', 12)
                    position = job.get('position', '')
                    company = job.get('company', '')
                    job_header = f"{position} at {company}"
                    self.pdf.cell(0, 6, job_header, ln=True)
                    
                    font = 'DejaVu' if self.font_available else 'Helvetica'
                    self.pdf.set_font(font, '', 10)
                    date_range = f"{job.get('start_date', '')} - {job.get('end_date', 'Present')}"
                    location = job.get('location', '')
                    date_loc = f"{date_range} | {location}" if location else date_range
                    self.pdf.cell(0, 5, date_loc, ln=True)
                    
                    self.pdf.ln(2)
                    self.pdf.set_font(font, '', 11)
                    description = job.get('description', '')
                    self.pdf.multi_cell(0, 5, str(description))
                    
                    if 'achievements' in job and job['achievements']:
                        self.pdf.ln(2)
                        achievements = job['achievements']
                        if isinstance(achievements, list):
                            for achievement in achievements:
                                self.pdf.cell(5, 5, chr(8226), ln=0)
                                self.pdf.multi_cell(0, 5, f" {str(achievement)}")
                        else:
                            self.pdf.multi_cell(0, 5, str(achievements))
                else:
                    font = 'DejaVu' if self.font_available else 'Helvetica'
                    self.pdf.set_font(font, '', 11)
                    self.pdf.multi_cell(0, 5, str(job))
                
                self.pdf.ln(5)
        else:
            font = 'DejaVu' if self.font_available else 'Helvetica'
            self.pdf.set_font(font, '', 11)
            self.pdf.multi_cell(0, 5, str(experience))
            
        self.pdf.ln(5)
        
    def add_education(self, education):
        """Add education section"""
        if not education:
            return
            
        self.add_section_heading("Education")
        
        if isinstance(education, list):
            for edu in education:
                if isinstance(edu, dict):
                    font = 'DejaVuBold' if self.font_available else 'Helvetica'
                    self.pdf.set_font(font, '', 12)
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', '')
                    edu_header = f"{degree}, {institution}"
                    self.pdf.cell(0, 6, edu_header, ln=True)
                    
                    font = 'DejaVu' if self.font_available else 'Helvetica'
                    self.pdf.set_font(font, '', 10)
                    date_range = f"{edu.get('start_date', '')} - {edu.get('end_date', '')}"
                    location = edu.get('location', '')
                    date_loc = f"{date_range} | {location}" if location else date_range
                    self.pdf.cell(0, 5, date_loc, ln=True)
                    
                    if 'description' in edu and edu['description']:
                        self.pdf.ln(2)
                        self.pdf.set_font(font, '', 11)
                        self.pdf.multi_cell(0, 5, str(edu['description']))
                else:
                    font = 'DejaVu' if self.font_available else 'Helvetica'
                    self.pdf.set_font(font, '', 11)
                    self.pdf.multi_cell(0, 5, str(edu))
                
                self.pdf.ln(5)
        else:
            font = 'DejaVu' if self.font_available else 'Helvetica'
            self.pdf.set_font(font, '', 11)
            self.pdf.multi_cell(0, 5, str(education))
            
        self.pdf.ln(5)
        
    def add_certifications(self, certifications):
        """Add certifications section"""
        if not certifications:
            return
            
        self.add_section_heading("Certifications")
        font = 'DejaVu' if self.font_available else 'Helvetica'
        self.pdf.set_font(font, '', 11)
        
        if isinstance(certifications, list):
            for cert in certifications:
                self.pdf.cell(5, 5, chr(8226), ln=0)
                self.pdf.multi_cell(0, 5, f" {str(cert)}")
        else:
            self.pdf.multi_cell(0, 5, str(certifications))
            
        self.pdf.ln(5)
    
    def generate_from_json(self, json_data):
        """Generate a PDF resume from JSON data"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
            
        if not isinstance(data, dict):
            raise ValueError("resume_data must be a dictionary")
            
        self.add_header(data.get('name', 'Unknown Name'), data.get('title', ''))
        
        if 'contact' in data and isinstance(data['contact'], dict):
            self.add_contact_info(data['contact'])
            
        if 'summary' in data:
            self.add_summary(data['summary'])
            
        if 'skills' in data:
            self.add_skills(data['skills'])
            
        if 'experience' in data:
            self.add_experience(data['experience'])
            
        if 'education' in data:
            self.add_education(data['education'])
            
        if 'certifications' in data:
            self.add_certifications(data['certifications'])
            
    def save(self, filename='resume.pdf'):
        """Save the PDF to a file"""
        try:
            self.pdf.output(filename)
            if os.path.exists(filename):
                return filename
            return None
        except Exception as e:
            print(f"Error saving PDF: {str(e)}")
            return None

def generate_resume_pdf(json_data, output_file='resume.pdf'):
    """Generate a resume PDF from JSON data"""
    try:
        # Create fonts directory if it doesn't exist
        os.makedirs('static/fonts', exist_ok=True)
        
        # Check if font files exist
        font_files = [
            ('DejaVuSansCondensed.ttf', 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSansCondensed.ttf'),
            ('DejaVuSansCondensed-Bold.ttf', 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSansCondensed-Bold.ttf')
        ]
        
        for font_file, font_url in font_files:
            font_path = f'static/fonts/{font_file}'
            if not os.path.exists(font_path):
                try:
                    print(f"Downloading font {font_file}...")
                    urllib.request.urlretrieve(font_url, font_path)
                except Exception as e:
                    print(f"Failed to download font {font_file}: {str(e)}")
                    # Fallback to generate_resume_pdf_simple
                    return generate_resume_pdf_simple(json_data, output_file)
        
        # Create and configure the PDF
        resume = ResumePDF()
        resume.generate_from_json(json_data)
        return resume.save(output_file)
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        print(traceback.format_exc())
        # Fallback to simple version
        return generate_resume_pdf_simple(json_data, output_file)

def generate_resume_pdf_simple(json_data, output_file='resume.pdf'):
    """Generate a simple resume PDF from JSON data"""
    try:
        # Parse JSON if it's a string
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
            
        if not isinstance(data, dict):
            raise ValueError("resume_data must be a dictionary")
            
        # Create a simple PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add name and title
        pdf.set_font('Helvetica', 'B', 16)
        name = data.get('name', 'Unknown Name')
        pdf.cell(0, 10, name, ln=True, align='C')
        
        if 'title' in data:
            pdf.set_font('Helvetica', '', 12)
            pdf.cell(0, 10, str(data['title']), ln=True, align='C')
        
        # Add contact info
        if 'contact' in data and isinstance(data['contact'], dict):
            pdf.ln(5)
            pdf.set_font('Helvetica', '', 10)
            contact = data['contact']
            
            contact_text = ""
            if 'email' in contact:
                contact_text += f"Email: {contact['email']}   "
            if 'phone' in contact:
                contact_text += f"Phone: {contact['phone']}   "
                
            pdf.cell(0, 5, contact_text, ln=True, align='C')
        
        # Add summary
        if 'summary' in data:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, 'Summary', ln=True)
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 5, str(data['summary']))
        
        # Add skills
        if 'skills' in data:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, 'Skills', ln=True)
            pdf.set_font('Helvetica', '', 10)
            
            if isinstance(data['skills'], list):
                skills_text = ", ".join(str(skill) for skill in data['skills'])
            else:
                skills_text = str(data['skills'])
                
            pdf.multi_cell(0, 5, skills_text)
        
        # Add experience
        if 'experience' in data:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, 'Experience', ln=True)
            pdf.set_font('Helvetica', '', 10)
            
            if isinstance(data['experience'], list):
                for exp in data['experience']:
                    if isinstance(exp, dict):
                        position = exp.get('position', '')
                        company = exp.get('company', '')
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.cell(0, 5, f"{position} at {company}", ln=True)
                        pdf.set_font('Helvetica', '', 10)
                        
                        date_range = f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}"
                        pdf.cell(0, 5, date_range, ln=True)
                        
                        if 'description' in exp:
                            pdf.multi_cell(0, 5, str(exp['description']))
                        
                        pdf.ln(3)
                    else:
                        pdf.multi_cell(0, 5, str(exp))
                        pdf.ln(3)
            else:
                pdf.multi_cell(0, 5, str(data['experience']))
        
        # Add education
        if 'education' in data:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, 'Education', ln=True)
            pdf.set_font('Helvetica', '', 10)
            
            if isinstance(data['education'], list):
                for edu in data['education']:
                    if isinstance(edu, dict):
                        degree = edu.get('degree', '')
                        institution = edu.get('institution', '')
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.cell(0, 5, f"{degree}, {institution}", ln=True)
                        pdf.set_font('Helvetica', '', 10)
                        
                        date_range = f"{edu.get('start_date', '')} - {edu.get('end_date', '')}"
                        pdf.cell(0, 5, date_range, ln=True)
                        
                        if 'description' in edu:
                            pdf.multi_cell(0, 5, str(edu['description']))
                        
                        pdf.ln(3)
                    else:
                        pdf.multi_cell(0, 5, str(edu))
                        pdf.ln(3)
            else:
                pdf.multi_cell(0, 5, str(data['education']))
        
        # Add certifications
        if 'certifications' in data:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, 'Certifications', ln=True)
            pdf.set_font('Helvetica', '', 10)
            
            if isinstance(data['certifications'], list):
                for cert in data['certifications']:
                    pdf.cell(5, 5, chr(127), ln=0)
                    pdf.multi_cell(0, 5, f" {str(cert)}")
            else:
                pdf.multi_cell(0, 5, str(data['certifications']))
        
        # Save the PDF
        pdf.output(output_file)
        if os.path.exists(output_file):
            return output_file
        return None
        
    except Exception as e:
        print(f"Error generating simple PDF: {str(e)}")
        print(traceback.format_exc())
        return None