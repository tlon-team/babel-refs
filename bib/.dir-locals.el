;;; Directory Local Variables            -*- no-byte-compile: t -*-
;;; For more information see (info "(emacs) Directory Variables")
((bibtex-mode . ((eval . (add-hook 'after-save-hook #'tlon-auto-clean-entry nil t))))
 (json-mode . ((jinx-languages . "ar es fr it ") ; Japanese, Korean not supported by Aspell
	       (flycheck-languagetool-language . "es"))))
