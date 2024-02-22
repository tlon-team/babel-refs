;;; Directory Local Variables            -*- no-byte-compile: t -*-
;;; For more information see (info "(emacs) Directory Variables")
((bibtex-mode . ((eval . (add-hook 'after-save-hook #'tlon-babel-auto-clean-entry nil t)))))
