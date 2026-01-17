import requests
from bs4 import BeautifulSoup
import re
import os
import sys

# --- CONFIGURATION ---
# Static links to the web pages
film_link = "https://en.wikipedia.org/wiki/List_of_Star_Wars_films"
series_link = "https://en.wikipedia.org/wiki/List_of_Star_Wars_television_series"
characters_link = "https://en.wikipedia.org/wiki/List_of_Star_Wars_characters"
mandalorian_link = "https://en.wikipedia.org/wiki/The_Mandalorian"
planets_link = "https://en.wikipedia.org/wiki/List_of_Star_Wars_planets_and_moons"

# --- HELPER FUNCTIONS ---

def get_soup(url):
    """
    Fetches a URL pretending to be a browser to avoid being blocked.
    Returns the BeautifulSoup object.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for 403/404 errors
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_main_content(soup):
    """
    Robustly finds the main content div, trying multiple selectors.
    """
    if not soup:
        return None
        
    # Standard Wikipedia article content
    content = soup.find("div", {"class": "mw-parser-output"})
    if content:
        return content
        
    # Fallback for some list pages
    content = soup.find("div", {"class": "mw-content-ltr"})
    return content

def convert_page_to_text(html_tag, title_tags, keep_headers, headers, page_title):
    regex_headers = ("|".join(headers))
    
    # Unwrap meta tags
    meta_tags = html_tag.find_all("meta")
    for meta_tag in meta_tags:
        meta_tag.unwrap()

    full_page_text = ""
    last_tag_name = None
    ignore_paragraph = False

    full_page_text += f"<h1>{page_title}</h1>"

    # Removing span tags with class IPA
    for tag in html_tag.find_all("span", {"class": "IPA"}):
        tag.decompose()

    for child_tag in html_tag.children:
        if child_tag.name == "p":
            if not ignore_paragraph:
                if last_tag_name is None or last_tag_name != "p":
                    full_page_text += "<p>"
                full_page_text += child_tag.text
                last_tag_name = "p"
        else:
            if last_tag_name is not None and last_tag_name == "p":
                full_page_text += "</p>"
            last_tag_name = child_tag.name

            # Skip ignored headers
            if child_tag.name == "h2" and re.search(regex_headers, child_tag.text, flags=re.IGNORECASE):
                ignore_paragraph = not keep_headers
            elif child_tag.name == "h2":
                ignore_paragraph = keep_headers

            if not ignore_paragraph and child_tag.name in title_tags:
                full_page_text += f'<{child_tag.name}>{child_tag.text}</{child_tag.name}>'

    # FIXED REGEX: Added 'r' to strings to fix SyntaxWarnings
    full_page_text = re.sub(r"\[.+?\]", "", full_page_text)
    full_page_text = re.sub(r"&(.)+;", "", full_page_text)
    full_page_text = re.sub(r"\((.)*Japanese(.)*\)", "", full_page_text)

    return full_page_text

def save_pages(web_pages_texts, file_names, directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

    for file_name, text in zip(file_names, web_pages_texts):
        # Clean filename to remove illegal characters
        safe_name = re.sub(r'[\\/*?:"<>|]', "", file_name)
        file_path = os.path.join(directory, safe_name + ".html")

        with open(file_path, "w", encoding='utf-8') as html_file:
            html_file.write(text)

def wikipedia_extract_link(content_tag, link_name_regex):
    links = content_tag.find_all("a")
    link_dict = {tag.text: tag.get("href") for tag in links}

    compiled_wiki_regex = re.compile("wiki")
    remove_key = []

    for key, link in link_dict.items():
        if link is None or not re.search(compiled_wiki_regex, link):
            remove_key.append(key)

    for k in remove_key:
        del link_dict[k]

    relevant_links = []
    for key, value in link_dict.items():
        if re.search(link_name_regex, key):
            relevant_links.append(value)

    # FIXED REGEX
    for idx, link in enumerate(relevant_links):
        relevant_links[idx] = re.sub(r"#(.+)$", "", link)

    relevant_links = list(set(relevant_links))

    for idx, link in enumerate(relevant_links):
        if not link.startswith("http"):
            relevant_links[idx] = "https://en.wikipedia.org" + link

    return relevant_links

def extract_page_content(link_list, keep_headers_bool, headers, title_tags):
    web_pages_texts = []
    file_names = []

    print(f"   -> Extracting content from {len(link_list)} sub-pages...")
    
    for link in link_list:
        soup = get_soup(link)
        if not soup: continue
            
        div_content = get_main_content(soup)
        if not div_content: continue
        
        # Safe extraction of title
        title_tag = soup.find("h1", {"id": "firstHeading"})
        page_title = title_tag.text if title_tag else "Unknown Title"

        web_pages_texts.append(convert_page_to_text(div_content, title_tags, keep_headers_bool, headers, page_title))

        # Extract filename from URL
        match = re.findall(r"/wiki/(.+)", link)
        if match:
            file_name = re.sub(":", "", match[0])
            file_names.append(file_name)

    return web_pages_texts, file_names

# --- MAIN EXPORT FUNCTIONS ---

def export_movies():
    print("🎬 Exporting Movies...")
    soup_film = get_soup(film_link)
    if not soup_film: return

    div_content = get_main_content(soup_film)
    if not div_content: return

    title_tags = ["h1", "h2", "h3", "h4", "h5"]
    ignore_headers = ["Reception", "Unproduced and abandoned projects", "Documentaries", "Notes", "See also", "References", "External links"]

    full_page_text = convert_page_to_text(div_content, title_tags, False, ignore_headers, "List of Star Wars films")
    save_pages([full_page_text], ["Movies"], directory="./web_pages/")

    film_title_regex = re.compile(r"Episode|Rogue One|The Clone Wars|^Solo: A Star Wars Story$", flags=re.IGNORECASE)
    relevant_links = wikipedia_extract_link(div_content, film_title_regex)

    keep_headers = ["Plot", "Cast"]
    web_pages_texts, file_names = extract_page_content(relevant_links, True, keep_headers, title_tags)
    save_pages(web_pages_texts, file_names, directory="./web_pages/")

def wikipedia_extract_character_link(html_tag):
    div_link_container = html_tag.find_all("div", {"role": "note"})
    links = []
    for div in div_link_container:
        a_tag = div.find("a")
        if a_tag:
            link_to_resource = a_tag["href"]
            full_link = "https://en.wikipedia.org" + link_to_resource
            links.append(full_link)
    return links

def export_characters():
    print("👤 Exporting Characters...")
    soup_chars = get_soup(characters_link)
    if not soup_chars: return

    div_content = get_main_content(soup_chars)
    if not div_content: return

    title_tags = ["h1", "h2", "h3", "h4", "h5"]
    ignore_headers = ["References", "External Links"]

    full_page_text = convert_page_to_text(div_content, title_tags, False, ignore_headers, "List of Star Wars characters")
    save_pages([full_page_text], ["Characters"], directory="./web_pages/")

    relevant_links = wikipedia_extract_character_link(div_content)
    web_pages_texts, file_names = extract_page_content(relevant_links, False, [], title_tags)
    save_pages(web_pages_texts, file_names, directory="./web_pages/")

def convert_page_series_to_text(html_tag, page_title):
    for tag in html_tag.find_all("span", {"class": "IPA"}):
        tag.decompose()

    full_page_text = ""
    full_page_text += f"<h1>{page_title}</h1>"
    full_page_text += "<p>"

    for child_tag in html_tag.children:
        if child_tag.name == "h2":
            full_page_text += "</p>"
            break
        if child_tag.name == "p":
            full_page_text += child_tag.text

    episode_titles = html_tag.find_all("td", {"class": "summary"})
    episode_summaries = html_tag.find_all("td", {"class": "description"})

    for title, summary in zip(episode_titles, episode_summaries):
        title_tag = f"<title>{title.text}</title>"
        summary_tag = f"<p>{summary.text}</p>"
        full_page_text += title_tag + summary_tag

    # FIXED REGEX
    full_page_text = re.sub(r"\[.+?\]", "", full_page_text)
    full_page_text = re.sub(r"&(.)+;", "", full_page_text)
    full_page_text = re.sub(r"\((.)*Japanese(.)*\)", "", full_page_text)

    return full_page_text

def extract_series_content(links):
    pages_texts = []
    file_names = []
    print(f"   -> Processing {len(links)} series pages...")

    for link in links:
        soup = get_soup(link)
        if not soup: continue

        div_content = get_main_content(soup)
        if not div_content: continue
        
        title_tag = soup.find("h1", {"id": "firstHeading"})
        page_title = title_tag.text if title_tag else "Unknown Series"

        page_text = convert_page_series_to_text(div_content, page_title)
        pages_texts.append(page_text)

        match = re.findall(r"/wiki/(.+)", link)
        if match:
            file_name = re.sub(":", "", match[0])
            file_names.append(file_name)

    return pages_texts, file_names

def retrieve_mandalorian_links():
    soup = get_soup(mandalorian_link)
    if not soup: return []
    
    div_content = get_main_content(soup)
    if not div_content: return []

    links_to_mandalorian_seasons = div_content.find_all("a", {"title": re.compile(r"^The Mandalorian season*")})
    links = [link["href"] for link in links_to_mandalorian_seasons]

    after_hash_regex = re.compile(r"#(.)*")
    filtered_links = [re.sub(after_hash_regex, "", link) for link in links]
    filtered_links = list(set(filtered_links))
    filtered_links = ["https://en.wikipedia.org" + link if not link.startswith("http") else link for link in filtered_links]

    return filtered_links

def export_series():
    print("📺 Exporting Series...")
    soup_series = get_soup(series_link)
    if not soup_series: return

    div_content = get_main_content(soup_series)
    if not div_content: 
        print("Error: Could not find main content for Series.")
        return

    div_link_container = div_content.find_all("div", {"role": "note"})
    links = []
    for div in div_link_container:
        link_to_resource = div.find("a")
        if link_to_resource:
            full_link = "https://en.wikipedia.org" + link_to_resource["href"]
            links.append(full_link)

    mandalorian_links = retrieve_mandalorian_links()
    links.extend(mandalorian_links)

    web_pages_texts, file_names = extract_series_content(links)
    save_pages(web_pages_texts, file_names, directory="./web_pages/")

def export_planets():
    print("🪐 Exporting Planets...")
    soup = get_soup(planets_link)
    if not soup: return

    div_content = get_main_content(soup)
    if not div_content: 
        print("Error: Could not find main content for Planets.")
        return

    file_names = []
    text_pages = []

    # Astrography
    astrography_text = "<h1>Canon Astrography of Star Wars</h1>"
    astro_span = div_content.find("span", {"id": "Star_Wars_canon_astrography"})
    
    if astro_span:
        h2_astrography = astro_span.parent
        next_tag = h2_astrography.next_sibling
        while next_tag and next_tag.name != "h2":
            if next_tag.name in ["p", "ul", "dl"]:
                astrography_text += next_tag.text
            next_tag = next_tag.next_sibling
        
        file_names.append("Astrography")
        text_pages.append(astrography_text)

    # Planets Table
    tables = div_content.find_all("table", {"class": "wikitable"})
    if tables:
        planet_table = tables[0]
        new_line_regex = re.compile(r"\n")

        for row in planet_table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < 5: continue
            
            planet_name = cols[0].text
            descr = cols[4].text
            
            filtered_name = re.sub(new_line_regex, "", planet_name).strip()
            filtered_descr = re.sub(new_line_regex, "", descr).strip()

            text_page = f"<h1>{filtered_name}</h1><p>{filtered_descr}</p>"
            text_pages.append(text_page)
            file_names.append(filtered_name)

    save_pages(text_pages, file_names, directory="./web_pages/")

if __name__ == "__main__":
    export_planets()
    export_series()
    export_movies()
    export_characters()
    print("✅ All Exports Complete!")