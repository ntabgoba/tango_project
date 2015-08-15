from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout 
from datetime import datetime
from rango.bing_search import run_query 
from django.shortcuts import redirect

# Create your views here.
def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'pages': page_list}
	visits = request.session.get('visits')
	if not visits:
		visits = 1
	reset_last_visit_time = False
	last_visit = request.session.get('last_visit')
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
		if (datetime.now() - last_visit_time).days > 5:
			visits = visits + 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True
	if reset_last_visit_time:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits
	context_dict['visits'] = visits
	response = render(request, 'rango/index.html', context_dict)
	return response

def about(request):
	if request.session.get('visits'):
		count = request.session.get('visits')
	else:
		count = 0
	context_dict = {'boldmessage': 'here is the about page', 'visits': count}
	return render(request, 'rango/about.html',context_dict)

def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)

	 
	## Query the database for a list of ALL categories currently stored.
    ## Order the categories by no. likes in descending order.
    ## Retrieve the top 5 only - or all if less than 5.
    ## Place the list in our context_dict dictionary which will be passed to the template engine.
	## Construct a dictionary to pass to the template engine as its context.
    ## Note the key boldmessage is the same as {{ boldmessage }} in the template!
   

    ## Return a rendered response to send to the client.
    ## We make use of the shortcut function to make our lives easier.
    ## Note that the first parameter is the template we wish to use.

def add_category(request):
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form
		if form.is_valid():
			# Save teh new cat to the database
			form.save(commit=True)

			#call the index() view and show user the homepage
			return index(request)

		else:
			print form.errors

	else:
		form = CategoryForm()
	return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
	try:
		cat = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		cat = None
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				#probably better to use a redirect here.
				return category(request, category_name_slug)
		else:
			print form.errors
	else:
		form = PageForm()
	context_dict = { 'form':form, 'category':cat, 'category_name_slug':category_name_slug }
	return render(request, 'rango/add_page.html', context_dict)

def search(request):
	result_list = []
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			result_list = run_query(query)
	return render(request, 'rango/search.html',{'result_list': result_list})

def track_url(request):
	page_id = None
	url = '/rango/'
	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views + 1
				page.save()
				url = page.url
			except:
				pass
	return redirect(url)

@login_required
def like_category(request):
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']
	likes = 0
	if cat_id:
		cat = Category.objects.get(id=int(cat_id))
		if cat:
			likes = cat.likes + 1
			cat.likes = likes
			cat.save()
	return HttpResponse(likes)








	
