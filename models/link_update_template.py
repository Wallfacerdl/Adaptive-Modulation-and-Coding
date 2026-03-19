from __future__ import annotations

from abc import ABC, abstractmethod


class LinkUpdateTemplate(ABC):
    """Template method for one TTI link update."""

    def update_link(self) -> None:
        self._before_update()
        self._update_channel()
        self._mark_transmission()
        self._update_snr()
        self._update_cqi()
        self._update_mcs()
        self._update_bler()
        self._optimize_outer_loop()
        self._after_update()

    def _before_update(self) -> None:
        pass

    def _after_update(self) -> None:
        pass

    @abstractmethod
    def _update_channel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _mark_transmission(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _update_snr(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _update_cqi(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _update_mcs(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _update_bler(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _optimize_outer_loop(self) -> None:
        raise NotImplementedError
