import requests
from bs4 import BeautifulSoup
import time

def scrape_indeed_jobs(query, location="", url_override=None):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    if url_override:
        url = url_override
    else:
        url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.find_all("div", class_="job_seen_beacon")
    for card in cards[:5]:
        title = card.find("h2", class_="jobTitle")
        company = card.find("span", class_="companyName")
        location_elem = card.find("div", class_="companyLocation")
        desc = card.find("div", class_="job-snippet")
        link = card.find("a", href=True)
        if title and company and location_elem and desc and link:
            job = {
                "platform": "Indeed",
                "title": title.text.strip(),
                "company": company.text.strip(),
                "location": location_elem.text.strip(),
                "description": desc.text.strip(),
                "url": "https://www.indeed.com" + link['href']
            }
            jobs.append(job)
    return jobs

def scrape_glassdoor_jobs(query, location="", url_override=None):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    if url_override:
        url = url_override
    else:
        url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query.replace(' ', '+')}&locT=C&locId=0&locKeyword={location.replace(' ', '+')}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.find_all("li", class_="jl")
    for card in cards[:5]:
        title = card.find("a", class_="jobLink")
        company = card.find("div", class_="jobHeader")
        location_elem = card.find("span", class_="subtle loc")
        desc = card.find("div", class_="jobDescriptionContent")
        link = title['href'] if title else None
        if title and company and location_elem and desc and link:
            job = {
                "platform": "Glassdoor",
                "title": title.text.strip(),
                "company": company.text.strip(),
                "location": location_elem.text.strip(),
                "description": desc.text.strip(),
                "url": "https://www.glassdoor.com" + link
            }
            jobs.append(job)
    return jobs

def scrape_linkedin_jobs(query, location="", url_override=None):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    if url_override:
        url = url_override
    else:
        url = f"https://www.linkedin.com/jobs/search?keywords={query.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.find_all("li", class_="result-card")
    for card in cards[:5]:
        title = card.find("h3", class_="result-card__title")
        company = card.find("h4", class_="result-card__subtitle")
        location_elem = card.find("span", class_="job-result-card__location")
        link = card.find("a", href=True)
        if title and company and location_elem and link:
            job = {
                "platform": "LinkedIn",
                "title": title.text.strip(),
                "company": company.text.strip(),
                "location": location_elem.text.strip(),
                "description": "",  # LinkedIn job description requires additional requests or API
                "url": link['href']
            }
            jobs.append(job)
    return jobs

def scrape_freelancer_jobs(query):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.freelancer.com/jobs/{query.replace(' ', '-')}/"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.find_all("div", class_="JobSearchCard-item")
    for card in cards[:5]:
        title = card.find("a", class_="JobSearchCard-primary-heading-link")
        company = "Freelancer"
        location_elem = ""
        desc = card.find("p", class_="JobSearchCard-primary-description")
        link = title['href'] if title else None
        if title and desc and link:
            job = {
                "platform": "Freelancer",
                "title": title.text.strip(),
                "company": company,
                "location": location_elem,
                "description": desc.text.strip(),
                "url": "https://www.freelancer.com" + link
            }
            jobs.append(job)
    return jobs

def scrape_upwork_jobs(query):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.upwork.com/search/jobs/?q={query.replace(' ', '%20')}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.find_all("section", class_="air-card-hover")
    for card in cards[:5]:
        title = card.find("h4", class_="job-title")
        company = "Upwork"
        location_elem = ""
        desc = card.find("span", class_="break-word")
        link = card.find("a", href=True)
        if title and desc and link:
            job = {
                "platform": "Upwork",
                "title": title.text.strip(),
                "company": company,
                "location": location_elem,
                "description": desc.text.strip(),
                "url": link['href']
            }
            jobs.append(job)
    return jobs

def scrape_jobs(query, location="", skills=None):
    """
    Scrape jobs from multiple platforms and filter by skills if provided.

    Args:
        query (str): Job title or keywords.
        location (str): Location filter.
        skills (list or set): Skills keywords to filter jobs.

    Returns:
        list: Filtered list of job dictionaries.
    """
    jobs = []
    jobs.extend(scrape_indeed_jobs(query, location))
    time.sleep(1)
    jobs.extend(scrape_glassdoor_jobs(query, location))
    time.sleep(1)
    jobs.extend(scrape_linkedin_jobs(query, location))
    time.sleep(1)
    jobs.extend(scrape_freelancer_jobs(query))
    time.sleep(1)
    jobs.extend(scrape_upwork_jobs(query))

    if skills:
        skills_lower = set(skill.lower() for skill in skills)
        filtered_jobs = []
        for job in jobs:
            job_text = (job.get("title", "") + " " + job.get("description", "")).lower()
            if any(skill in job_text for skill in skills_lower):
                filtered_jobs.append(job)
        return filtered_jobs

    return jobs
