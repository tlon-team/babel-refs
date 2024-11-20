;;; Directory Local Variables            -*- no-byte-compile: t -*-
;;; For more information see (info "(emacs) Directory Variables")
((bibtex-mode . ((eval . (add-hook 'after-save-hook #'tlon-auto-clean-entry nil t))
		 (eval . (add-hook 'after-save-hook #'tlon-deepl-fix-encoding-persistent nil t))))
 (json-mode . ((jinx-languages . "ar es fr it")
	       (flycheck-languagetool-language . "es"))))
