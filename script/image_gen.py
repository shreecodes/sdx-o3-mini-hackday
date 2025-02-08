import replicate

models = {
    "recraft" : 'recraft-ai/recraft-v3-svg',
    "flux": 'black-forest-labs/flux-dev',
    "flux-s": 'black-forest-labs/flux-schnell',
}

# N.B. uncomment to view sources for original models
#for _, model in models.items():
#    print(f"https://replicate.com/{model}")


# N.B. file extension is *implied* by the model. `filename` is a *base* name (without extension)
def get_image(prompt: str, filename: str, model=models['flux-s']):
    extension = 'svg' if 'svg' in model else 'png'
    output  = replicate.run(
        model,
        input={'prompt': prompt}
    )
    # N.B. fix ambiguous model result (list[fo] vs fo)
    if isinstance(output, list):
        output = output[0]
    # Save the generated image
    with open(f"static/{filename}.{extension}", 'wb') as f:
        f.write(output.read())

get_logo = lambda prompt, fn: get_image(prompt, fn, model=models['recraft'])


logo_prompt="Striking neon, minimalist, logo of a dog-walking business called 'Pawfect Walks'`"
get_image(logo_prompt, 'image')
get_logo(logo_prompt, 'logo')
