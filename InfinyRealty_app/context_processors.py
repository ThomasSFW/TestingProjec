# from .models import MenuCategory
from .models import MenuTabs
from .models import MenuCategories
from .models import MenuSubCategories

# def category_renderer(request):
	# return{
	    # 'categories': MenuCategory.objects.all()
	# }  
    
def menutabs_renderer(request):
    return {	    
        'menutabs': MenuTabs.objects.using('qadind').all()
	}

def menucategories_renderer(request):
	return {
	    'menucategories': MenuCategories.objects.using('qadind').all()
	}

def menusubcategories_renderer(request):
	return {
	    'menusubcategories': MenuSubCategories.objects.using('qadind').all()
	}




