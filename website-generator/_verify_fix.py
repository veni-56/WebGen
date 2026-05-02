import sys, os
sys.path.insert(0, '.')
import generator as g

config = {'project_type':'ecommerce','site_name':'TestShop','primary_color':'#e91e63','secondary_color':'#ff5722','font':'Poppins'}
result = g.build_project('test_earnings_fix', config)
app_py = g.read_file('test_earnings_fix', 'app.py')

# Check the fix
has_broken = 'total_earned=total,' in app_py and 'earnings.html' in app_py
has_fixed  = "rows=rows,total=total," in app_py
print('Broken pattern gone:', not has_broken)
print('Fixed pattern present:', has_fixed)

compile(app_py, 'app.py', 'exec')
print('Syntax check: PASSED')
