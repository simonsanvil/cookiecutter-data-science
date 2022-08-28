<%!
    from {{ cookiecutter.python_package }}.__init__ import __version__
    from datetime import datetime
    from pathlib import Path
    now = datetime.now()
    __author__ = "{{ cookiecutter.author_name }}"
    if __author__.strip()=="Your name (or your organization/company/team)":
        __author__ = None

    git_branch = ""
    if Path(".git").is_dir():
        head_dir = Path(".") / ".git" / "HEAD"
        with head_dir.open("r") as f: 
            content = f.read().splitlines()
        for line in content:
            if line[0:4] == "ref:":
                git_branch = line.partition("refs/heads/")[2]
%>
<!doctype html>
%if git_branch:
<a href="#">
## <a href="#" target="_blank">
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-git-branch"><line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1-9 9"></path></svg>
    <p>{{ cookiecutter.python_package }} v${__version__}</p>
    <span>(${git_branch})</span>
</a>
%endif
<p>
<p>
%if __author__:
<p>Author: <a href="#" target="_blank">${__author__}</a></p>
## <p>License: <a href="http://www.gnu.org/licenses/gpl.html">GNU General Public License</a></p>
<p>Copyright: &copy; <?php echo date("Y"); ?>${now.year}, ${__author__}</p>
%endif
<p>Last Updated: ${now.strftime('%b, %Y')}</p>

## <p>
##     <a href="http://validator.w3.org/check?uri=referer">
##         <img src="http://www.w3.org/Icons/valid-xhtml10" alt="Valid XHTML 1.0 Strict" height="31" width="88" />
##     </a>
## </p>
## <p>
##     <a href="http://jigsaw.w3.org/css-validator/check/referer">
##         <img style="border:0;width:88px;height:31px" src="http://jigsaw.w3.org/css-validator/images/vcss" alt="Valid CSS!" />
##     </a>
## </p>
## <p>
##     <a href="http://www.mozilla.org/products/firefox/">
##         <img src="http://www.mozilla.org/products/firefox/images/firefox-logo.png" alt="Firefox" height="31" width="88" />
##     </a>
## </p>
