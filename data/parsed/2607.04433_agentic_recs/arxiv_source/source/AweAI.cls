%%%%%%%%%
%
% Basic style file for AweAI open-access papers, internal reports, and unpublished
% papers.
%
% This template is adapted from the Google/Google DeepMind LaTeX template (google.cls).
% Original template by Google, licensed under CC BY-SA 4.0.
%
% This class allows for several options depending on the preferences of the authors.
% Use it in the following way, with the full set of option possible:
% \documentclass[11pt, a4paper, twocolumn, copyright, nonumbering,
% internal]{AweAI}
%
% Options:
%    - 11pt: Sets the normal font size of the text. Can be only 10, 11, 12pt.
%    - a4paper: Paper size. Usually would not adjust.
%    - twocolumn: Makes the paper into two column mode; single column by default.
%    - copyright: Add a copyright statement to the first page of the paper in the left footnote
%    - nonumbering: Uses unnumbered sections.
%    - confidential: add labels for internal only reports that should not be shared externally.
%           Can only use techreportnumber with this option.
%
% Date of Paper
%   The report is by default given the current date in the top right. If you want to fix the
%   date: add the date to your preamble with your own date as follows:
%   \renewcommand{\today}{1 January 2000}
%
% Confidentiality
%   Change the confidentiality statement for internal docs by adding this in the preamble
%   \renewcommand{\internalonly}{Confidential.}
%
%
% ----------------
% Licence: This template is released under the Creative Commons licence
% Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
%
%
% Known issues:
%   - Package todonotes does not work in the abstract
%
% %%%%%%%%%%%%%%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{AweAI} % no versioning; versioning does not work well with arxiv.

%%======== Package options and base class ========
\RequirePackage{xifthen}
\newboolean{nonumbering}
\newboolean{address}
\newboolean{copyright}
\newboolean{confidential}
\DeclareOption{nonumbering}{\setboolean{nonumbering}{true}}
\DeclareOption{address}{\setboolean{address}{true}}
\DeclareOption{copyright}{\setboolean{copyright}{true}}
\DeclareOption{confidential}{\setboolean{confidential}{true}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{extarticle}}
\ProcessOptions
\LoadClass{extarticle}

%%======== Packages Required ========
% Fonts and language
\AtEndOfClass{\RequirePackage[tracking=smallcaps]{microtype}}
\RequirePackage[utf8]{inputenc}
\RequirePackage[english]{babel}
\RequirePackage{amsthm, amsmath, amsfonts, amssymb}
\RequirePackage{cmap}
\RequirePackage[T1]{fontenc}
\RequirePackage{tgpagella}      % text
\RequirePackage{mathpazo}       % math & text (Palatino math)
\RequirePackage{inconsolata}    % tt font
% \renewcommand{\rmdefault}{cmr}
% --- Match bytedance_seed sans fonts ---
% \DeclareFontFamily{T1}{bytesans}{}
% \DeclareFontShape{T1}{bytesans}{m}{n}{<-> s * [1] seed/bytesans}{}
% \pdfmapline{+bytesans < seed/ByteSans-Bold.ttf <T1-WGL4.enc}
% \renewcommand{\sfdefault}{bytesans}%


% \DeclareFontFamily{T1}{bytesansmedium}{}
% \DeclareFontShape{T1}{bytesansmedium}{m}{n}{<-> s*[1] seed/bytesansmedium}{}
% \pdfmapline{+bytesansmedium < seed/ByteSans-Medium.ttf <T1-WGL4.enc}

\RequirePackage[dvipsnames]{xcolor}
\definecolor{metabg}{HTML}{F1F4F7}
\definecolor{seedblue}{HTML}{2E5AA8}

\RequirePackage[colorlinks=true, linkcolor=seedblue, citecolor=seedblue, urlcolor=seedblue]{hyperref}

\RequirePackage{url}
\RequirePackage{pifont}
\RequirePackage[most]{tcolorbox}
\RequirePackage{textcomp}
\RequirePackage[overload]{textcase}
%\RequirePackage{balance}
%% *Graphics, tables and other formatting
\RequirePackage{graphicx}
\RequirePackage{colortbl}
\RequirePackage{booktabs}
\RequirePackage{changepage}
\RequirePackage{enumitem} % For reducing bullet list item separation
\RequirePackage{tabularx}
\RequirePackage{datetime}
% Headers and footers
\RequirePackage{fancyhdr}  % custom headers/footers
\RequirePackage{lastpage}  % Number of pages in the document
% Lists and their spacing
\RequirePackage{enumitem}
\setlist[itemize]{noitemsep}
\setlist[enumerate]{noitemsep}
% Title, Abstract, Bibliography
\RequirePackage[explicit]{titlesec}
\RequirePackage{bibentry}
\RequirePackage{mdframed}
\RequirePackage{caption}
\RequirePackage{needspace}
\RequirePackage{soul}
\RequirePackage{kvoptions}
% Tables
\RequirePackage{subcaption}
\RequirePackage{array}
\RequirePackage{makecell}
\RequirePackage[nameinlink]{cleveref}
% Math
\RequirePackage{bbm}


%%======== Can use any of these fonts ========
%\RequirePackage{charter}
%\RequirePackage[scaled]{helvet}
%\RequirePackage{bookman}
%\RequirePackage{times}
%\RequirePackage[default]{opensans} %fosfamily
%\usepackage{antpolt}
% Math fonts
%\RequirePackage{mathpazo} % Palatino
%\usepackage{euler} % for math fints

% Use Bitstream Charter as the main font. Does not include a typewriter font.
% \RequirePackage{XCharter}
% \RequirePackage[xcharter,bigdelims,vvarbb]{newtxmath}

% Use the typewriter font from lmodern, scaled up to match Charter's xheight.
% You may wish to add the "p" option to use the proportional font instead of
% the monospaced one, which might look nicer in cases where you do not need
% aligned columns
% \RequirePackage[scaled=1.1]{zlmtt}

%%======== Margins and column spacing ========
\RequirePackage[left=2.2cm,%
right=2.2cm,%
top=3cm,%
bottom=3cm,%
headheight=40pt,%
headsep=20pt,%
%showframe, % for testing
a4paper]{geometry}%
\setlength{\columnsep}{15pt} % Distance between the two columns of text
%\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5\baselineskip}

%% *Custom font sizes and styles
\newcommand{\watermarkfont}{\color{black50}\normalfont\fontsize{10}{12}\selectfont}
\newcommand{\headerfont}{\normalfont\sffamily\fontsize{8}{10}\selectfont}
\newcommand{\titlefont}{\color{black}\normalfont\bfseries\fontsize{18}{23}\selectfont}
\newcommand{\datesfont}{\normalfont\sffamily\itshape\fontsize{8}{10}\selectfont}
\newcommand\urlheaderfont{\color{blue}\fontsize{8}{10}\selectfont}
\newcommand{\absfont}{\linespread{1.2}\fontsize{10}{12}\selectfont}
\newcommand{\keywordstitlefont}{\bfseries\linespread{1.2}\fontsize{8}{10}\selectfont}
\newcommand{\keywordsfont}{\itshape\linespread{1.2}\fontsize{11}{12}\selectfont}
\newcommand{\copyrightfont}{\normalfont\fontsize{7}{9}\selectfont}
\newcommand{\footerfont}{\color{black}\normalfont\fontsize{8}{10}\selectfont}
\newcommand{\subjectfont}{\color{white}\bfseries\fontsize{10}{12}\selectfont}
\newcommand{\headingfont}{\color{black}\bfseries\fontsize{13}{14}\selectfont}

\newcommand{\keywords}[1]{\def\@keywords{#1}}
\newtoks\correspondingauthor
\newtoks\paperurl
\newtoks\reportnumber

% Dates and Times for footer
% ISO-8601 date format
\newdateformat{monthyeardate}{\THEYEAR-\twodigit{\THEMONTH}-\twodigit{\THEDAY}}

\setcounter{secnumdepth}{3}
\ifthenelse{\boolean{nonumbering}}{\setcounter{secnumdepth}{0}}{}

%%========  Author and affiliation ========
\RequirePackage{authblk}
\setcounter{Maxaffil}{0}
\setlength{\affilsep}{0.2em}
\renewcommand\Authfont{\normalfont\bfseries\fontsize{9}{13}\selectfont}
\renewcommand\Affilfont{\normalfont\fontsize{8}{10}\selectfont}
\makeatletter
\renewcommand\AB@affilsepx{, \protect\Affilfont}
\makeatother
\renewcommand\Authands{ and }

\newcommand{\internalonly}{\hl{Confidential---Do not share or forward externally}}
% \newcommand{\copyrightext}{\footerfont \textcopyright\, \the\year{} AweAI. All rights reserved}

%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%


%%======== Set template and Logo ========
% --- Provide User Command for PA Name ---

\newcommand{\pafullname}{} % store the PA name

% --- Process Standard Class Options ---
% Still useful for standard options like 10pt, 11pt, etc.
\DeclareOption* {\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax % Process standard options like 10pt, etc.

% --- Default Option ---
\def\@selectedlogo{0} % Default to no logo
\newcommand{\uselogo}[1]{#1}
\renewcommand{\pafullname}{AweAI}%

% --- Handle Unrecognized Options ---
% Pass any other options (like '12pt', 'twoside') to the base class ('article')
\DeclareOption* {\PassOptionsToClass{\CurrentOption}{article}}

% --- Process Options ---
% Execute the code associated with the options provided (or the default)
\ProcessOptions\relax

% --- Provide User Command for Company Name ---
% Define a user-friendly command to access the stored full company name
% This should be done *after* \ProcessOptions
\newcommand{\thepa}{\pafullname}


%%======== Header and Footer Content ========
% Header and Footer for the first page
\pagestyle{fancy}   % Enables the custom headers/footers

\fancypagestyle{firststyle}{

    \fancyhead[R]{%
        \ifdefined\paperurl
        \if\relax\the\paperurl\relax \else
            \href{\the\paperurl}{\urlheaderfont \itshape \the\paperurl}\\ \fi
        \else
        \fi
        {\footerfont\itshape\monthyeardate\today}
        \ifthenelse{\boolean{confidential}}{\\ \footerfont \internalonly}{}
    }

    % \fancyhead[R]{}

    \fancyhead[C]{}

    % -------- 页脚：保持你原来的不动 --------
    \fancyfoot[L]{
    \footerfont\itshape
      % \ifdefined\footerlinks
      %   {\normalfont\footerlinks}\\
      % \fi
        \ifdefined\correspondingauthor
        \if\relax\detokenize\expandafter{\the\correspondingauthor}\relax
      \else
        \footerfont\itshape {Emails: \the\correspondingauthor\\}% Corresponding author:
      \fi
    \fi
        % % \ifthenelse{\boolean{copyright}}{\copyrightext}{}
    }

    \fancyfoot[R]{
        \ifthenelse{\boolean{confidential}}{
        \ifdefined\reportnumber
        \if\relax\the\reportnumber\relax
        \else \footerfont\itshape  {\footerfont \thepa{} Technical Report \the\reportnumber} \fi
        \else \fi
        }{\footerfont\bfseries\relax}
    }
    \fancyfoot[C]{
        \footerfont\bfseries\relax}
}

% Header and Footer for pages from 2 onwards
\fancyhead[L,R]{}
\makeatletter
\fancyhead[C]{\footerfont \@title}
% \fancyhead[R]{
% 	\ifthenelse{\boolean{confidential}}{\footerfont \internalonly}{}
% }
\makeatother
\fancyfoot[C]{}
% \fancyfoot[L]{
% 	\ifthenelse{\boolean{confidential}}{\footerfont \internalonly\newline
% 		\ifdefined\reportnumber
% 		\if\relax\the\reportnumber\relax
% 		\else \footerfont {\thepa{} TR-\the\reportnumber} \fi
% 		\else \fi}{\footerfont\bfseries\relax}
% }
\fancyfoot[L]{
	\ifthenelse{\boolean{confidential}}{\footerfont \internalonly}{\footerfont\bfseries\relax}
}
\fancyfoot[R]{\footerfont 	
    %\ifdefined\reportnumber
	%\if\relax\the\reportnumber\relax
	%\else \footerfont\itshape  {\footerfont \thepa{} Technical Report \the\reportnumber} \fi
	%\else \fi \hspace{10mm} 
	\thepage}

% Header and footer rules (coloured).
\renewcommand{\headrulewidth}{1pt}
\renewcommand{\footrulewidth}{1pt}
\let\DefaultHeadRule\headrule
\let\DefaultFootRule\footrule
\renewcommand{\headrule}{\color{gray}\DefaultHeadRule}
\renewcommand{\footrule}{\textcolor{gray}{\DefaultFootRule}}

\renewenvironment{abstract}
{\par\noindent\\  \ignorespaces}
{\par\bigskip}

%%========  Bibliography using bibtex ========
%\RequirePackage[backend=biber,
%    style=authoryear,
%    maxcitenames=1,
%    maxbibnames=10,
%    backref=true
%]{biblatex}
\addto{\captionsenglish}{\renewcommand{\refname}{References}}
\newcommand{\citeas}[1]{\Needspace*{8\baselineskip}\noindent\bibentry{#1}}
% Uncomment the next line if you want the  numbered refs to be "1." instead of "[1]".
%\makeatletter \renewcommand\@biblabel[1]{#1.} \makeatother

%%======== Abstract and section formatting ========
\def\xabstract{abstract}
\long\def\abstract#1\end#2{\def\two{#2}\ifx\two\xabstract
	\long\gdef\theabstract{\ignorespaces#1}
	\def\go{\end{abstract}}\else
\typeout{^^J^^J PLEASE DO NOT USE ANY \string\begin\space \string\end^^J
	COMMANDS WITHIN ABSTRACT^^J^^J}#1\end{#2}
\gdef\theabstract{\vskip12pt BADLY FORMED ABSTRACT: PLEASE DO
NOT USE {\tt\string\begin...\string\end} COMMANDS WITHIN
THE ABSTRACT\vskip12pt}\let\go\relax\fi
\go}

% Define an environment with abstract content and styling
\makeatletter
\newcommand{\abscontent}{
	\noindent
	\parbox{\dimexpr\linewidth}{\absfont \theabstract}
	\@ifundefined{@keywords}{}{
		\vskip1em \noindent \keywordsfont  Keywords: \@keywords}
}

\if@twocolumn%
\renewcommand{\maketitle}{
  \twocolumn[
    \begin{adjustwidth}{0pt}{24pt}

      % ---- Title OUTSIDE the gray box ----
      \begin{flushleft}
        {\raggedright \titlefont \@title\par}%
      \end{flushleft}
      \vskip11pt

      % ---- Gray box ONLY for author + abstract ----
      \tcbset{
        enhanced,
        frame hidden,
        arc=10pt,
        left=0.5cm,right=0.5cm,top=0.5cm,bottom=0.5cm,
        colback=metabg,
        before skip=0pt,
      }
      \begin{tcolorbox}
        \begin{flushleft}
          {\raggedright \@author\par}%
          \vskip12pt
        \end{flushleft}

        \abscontent
      \end{tcolorbox}
      \tcbset{reset}

    \end{adjustwidth}
    \vskip20pt%
  ]
  \thispagestyle{firststyle}
}%
\else% \@twocolumnfalse
\renewcommand{\maketitle}{\bgroup\setlength{\parindent}{0pt}
  \begin{adjustwidth}{0pt}{24pt}

    % ---- Title OUTSIDE the gray box ----
    \begin{flushleft}
      {\raggedright \titlefont \@title\par}%
    \end{flushleft}
    \vskip11pt

    % ---- Gray box ONLY for author + abstract ----
    \tcbset{
      enhanced,
      frame hidden,
      arc=10pt,
      left=0.5cm,right=0.5cm,top=0.5cm,bottom=0.5cm,
      colback=metabg,
      before skip=0pt,
    }
    \begin{tcolorbox}
      \begin{flushleft}
        {\raggedright \@author\par}%
        \vskip12pt
      \end{flushleft}

      \abscontent
    \end{tcolorbox}
    \tcbset{reset}

  \end{adjustwidth}
\egroup
\thispagestyle{firststyle}
}%
\fi
\makeatother

% ---- Match bytedance_seed heading style ----
\titleformat{\section}
{\fontsize{12}{10}\selectfont\rmfamily\bfseries\color{seedblue}}
{\thesection.}
{0.5em}
{#1}
[]

\titleformat{name=\section,numberless}
{\fontsize{12}{10}\selectfont\rmfamily\bfseries\color{seedblue}}
{}
{0em}
{#1}
[]

\titleformat{\subsection}
{\fontsize{11}{10}\selectfont\rmfamily\bfseries\color{seedblue}}
{\thesubsection.}
{0.5em}
{#1}
[]

\titleformat{name=\subsection,numberless}
{\fontsize{11}{10}\selectfont\rmfamily\bfseries\color{seedblue}}
{}
{0em}
{#1}
[]

\titleformat{\subsubsection}
{\normalsize\rmfamily\bfseries\color{seedblue}}
{\thesubsubsection.}
{0.5em}
{#1}
[]

\titlespacing*{\section}{0pc}{3ex plus4pt minus3pt}{5pt}
%\titlespacing*{\section}{0pc}{1ex }{\baselineskip}
\titlespacing*{\subsection}{0pc}{2.5ex plus3pt minus2pt}{2pt}
\titlespacing*{\subsubsection}{0pc}{2ex plus2.5pt minus1.5pt}{2pt}
%\titlespacing*{\paragraph}{0pc}{2ex plus2pt minus1pt}{0pt}

%%======== Captions in tables and figures ========
\DeclareCaptionLabelSeparator{pipe}{ $\vert$ }% or $\vert$
\captionsetup{labelfont={}, %{bf,sf},%
labelsep=space,%
figurename=Figure,%
labelsep=pipe,
singlelinecheck=off,%
%justification=centering
}
