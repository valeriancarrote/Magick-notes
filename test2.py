import ftfy


mojibake = 'files\ActivitÃ© â€“ Lâ€™offensive des Dardanelles (1).pdf'
hey = ftfy.fix_text(mojibake)

print(hey)

