Release! myLastFmPlayer

Finally I've had implemented an idea I had in my mind for ages. a desktop player for favorite songs from last.fm. You just enter the username of an account, where you like the "loved" list and it will download that list, resolve them on youtube, download then for eachtrack the best qualtiy audio and store it locally. Some quality of life features followed when the prototype was done: like sorting and filtering the track-list; themes, language support.
I had already protoypse for parts of the functionality: like web-scraping with beuatiful soup, downloads from youtube, PyQt-UI-apps, .. but never bothered to form a full fledged product. But here it is. Already vetted through week long usage. And I like it.
Noteworthy as well: this is not just an AI-project: I've applied all the good measurements t quality, whch iI would usually apply to a project of 17k LoC. Local and GitHub Actions Ci-pipelines from the beginnng; 99% test coverage, heavy use of linters, static code analysis and reviews; documentation on several levels (C4 for architecture and code with Sphinx), release packages, and so on.



Features:
* bootstrap music-consumption by just entering a last.fm-username: MLP will download the favorite tracks list, resolve them on youtube, download the audiostream for each track in the best available quality
* play all songs, randomize or filter by substring in artist or title
* prioritzize tracks for search/download/play by double-click
* scrobble them back to last.fm (OAuth)
* four themes from lilac to mint
* fully localized for Croatian, Mandarin, German, English and Ukrainian
* full bootstrap from repo to built & tested app via one shell-script
* eager and responsive development team ;)
* mature code base: 99% test coverage, passes common linters 100%; Sphinx code and C4 architecture documentation, GitHub Actions pipeline for continuous integration and releases; release packages; ..
* remix and adapt: GPLv3

Repo at https://github.com/marcelpetrick/myLastFmPlayer - feedback welcome.


