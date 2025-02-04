START_MESSAGE: str = "Hi there! I'm JobSeeker Bot, your friendly job search assistant.😊\n" \
                     "I'm here to help you find the perfect position.\n\n" \
                     "To stop chatting with me at any time, just send '/cancel'.\n\n"

POSITION_MESSAGE: str = "What kind of position are you looking for? ✨\n\n" \
                        "(e.g., Software Engineer, Data Scientist, Marketing Manager)"

POSITION_NOT_FOUND: str = "I couldn't find any positions matching your request. 😕\n" \
                          "Please try again"
multi_value_message: str = "Enter multiple values separated by commas (e.g., value1, value2, value3) ✍️"

LOCATION_MESSAGE: str = "Where are you hoping to find a position? 🌎\n" \
                        "(e.g., Rishon Lezion, New York City, San Francisco)\n\n" + multi_value_message

EXPERIENCE_MESSAGE: str = "How many years of professional experience do you have in this field? 💼\n"

EXPERIENCE_INVALID: str = "Oops! Please enter your experience in years as a number.😕\n" \
                          "For example, 2, 5, or 10."

JOB_AGE_MESSAGE: str = "How recent should the jobs be? ⏰\n\n" \
                       "(Enter the number of hours, e.g., 24 for last 24 hours, 168 for last week)"

# JOB_AGE_MESSAGE: str = "Within how many hours do you want to see jobs posted? ⏰\n" \
#                         "(Enter a number, e.g., 48 for the last 48 hours)"

JOB_AGE_INVALID: str = "Oops!\n Please enter a number for the number of hours. 😕\n" \
                       "For example, 24, 48, or 168."

FILTER_TILE_MESSAGE: str = "To help me narrow down your search, tell me about any NOT relevant tags or keywords.\n" \
                           "For example: 'remote', 'BI', 'python', 'machine learning', 'QA'.\n\n" + multi_value_message

THANK_YOU_MESSAGE: str = "Thank you for chatting with JobSeeker Bot!\n\n" \
                         "I can help you find jobs on LinkedIn, Glassdoor, and more."

SEARCH_MESSAGE: str = "To search for jobs on a specific site, simply send the site name:\n" \
                      "/linkedin\n" \
                      "/indeed\n" \
                      "/glassdoor\n" \
                      "/goozali\n\n" \
                      "Or, use the command /find to search across all supported job boards for a broader search.\n\n" \
                      "Let me know how I can assist you further! 😊"

BYE_MESSAGE: str = "Have a great day!✨\n" \
                   "I hope to assist you with your job search in the future.😊"

VERIFY_MESSAGE: str = "Did you choose: %s ? 🧐"

DEFAULT_MESSAGE = SEARCH_MESSAGE + "\n\nB.S🤔\n" \
                    "Use /myinfo to 👀 your data 😊"