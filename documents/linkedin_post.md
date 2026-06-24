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


----

Release: **myLastFmPlayer**

Weeks ago I finally implemented an idea that had been on my mind for years.

It is a desktop player for your favorite tracks from Last.fm.

Enter the username of a Last.fm account whose loved tracks you like. The app imports that list, resolves the tracks on YouTube, downloads the best available audio stream, and stores it locally.

Once the prototype worked, I added the quality-of-life features that make it useful every day: sorting and filtering, themes, and language support.

I already had prototypes for individual parts: web scraping with BeautifulSoup, YouTube downloads, and PyQt desktop UIs. What I had not done was turn them into a full product.

**This time, I did.**

I have used it daily for several weeks now, and I genuinely like the result.

I also approached it as a production-grade software project from the beginning: I applied the same engineering practices I would expect from a codebase of roughly 17k lines.

That includes local and GitHub Actions CI #pipelines, 99% test #coverage, linters, #staticCodeAnalysis, reviews, Sphinx code documentation, #C4architecture documentation, and release packages.

Licensed under GPLv3 — remix and adapt it.

The repository is here:  https://github.com/marcelpetrick/myLastFmPlayer **Feedback, issues, and ideas are welcome.**
