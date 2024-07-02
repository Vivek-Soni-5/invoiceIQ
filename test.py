import duckpy

user_agents = [
  "Mozilla/5.0 (X11; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
]

client = duckpy.Client(default_user_agents=user_agents)

try:
    results = client.search("amazfit")
    
    if results:
        link = results[0].url
    else:
        link = "No link Found"

except Exception as e:
    link = f"An error occurred: {e}"

print(link)
