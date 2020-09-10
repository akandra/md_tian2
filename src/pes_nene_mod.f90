!############################################################################
! This routine is part of
! md_tian2 (Molecular Dynamics Tian Xia 2)
! (c) 2014-2020 Daniel J. Auerbach, Svenja M. Janke, Marvin Kammler,
!               Sascha Kandratsenka, Sebastian Wille
! Dynamics at Surfaces Department
! MPI for Biophysical Chemistry Goettingen, Germany
! Georg-August-Universitaet Goettingen, Germany
!
! This program is free software: you can redistribute it and/or modify it
! under the terms of the GNU General Public License as published by the
! Free Software Foundation, either version 3 of the License, or
! (at your option) any later version.
!
! This program is distributed in the hope that it will be useful, but
! WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
! or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
! for more details.
!
! You should have received a copy of the GNU General Public License along
! with this program. If not, see http://www.gnu.org/licenses.
!############################################################################

module pes_nene_mod

    use constants
    use open_file, only : open_for_read
    use universe_mod
    use useful_things, only : split_string, lower_case

    implicit none


    character(len=max_string_length)   :: prog_path, inp_path
    character(len=max_string_length)   :: input_string, outforces_string, outenergy_string, prog_string, grep_string


    contains

    !later: Read in here the keywords for the high-dimensional neural network potentials (HDNNPs)
    subroutine read_nene(atoms, inp_unit)

        use run_config, only : simparams

        type(universe), intent(inout) :: atoms
        integer, intent(in) :: inp_unit

        integer :: nwords, ios = 0
        character(len=max_string_length) :: buffer
        character(len=max_string_length) :: words(100)
        integer  :: idx1, idx2, ntypes
        character(len=*), parameter :: err = "Error in read_nene: "

        ntypes = simparams%nprojectiles+simparams%nlattices

        read(inp_unit, '(A)', iostat=ios) buffer
        call split_string(buffer, words, nwords)

        if (nwords /= 4) stop err // "need four entries in interaction-defining lines"

        if (words(3) == "proj" .and. words(4) == "proj" .or. &
            words(3) == "proj" .and. words(4) == "latt" .or. &
            words(3) == "latt" .and. words(4) == "proj" .or. &
            words(3) == "latt" .and. words(4) == "latt") then

            idx1 = get_idx_from_name(atoms, words(1), is_proj=(words(3)=="proj"))
            idx2 = get_idx_from_name(atoms, words(2), is_proj=(words(4)=="proj"))

            if (atoms%pes(idx1,idx2) /= default_int) then
                print *, err // "pes already defined for atoms", words(1), words(3), words(2), words(4)
                stop
            end if

        else
            print *, err // "interaction must be defined via 'proj' and 'latt' keywords"
            stop
        end if

        ! set the pes type in the atoms object
        atoms%pes(idx1,idx2) = pes_id_nene
        atoms%pes(idx2,idx1) = pes_id_nene


        do
            read(inp_unit, '(A)', iostat=ios) buffer
            call split_string(buffer, words, nwords)

            ! pes block terminated, exit
            if (nwords == 0 .or. ios /= 0) then
                exit

            ! something went wrong
            else if (nwords /= 2) then
                stop "Error in the PES file: PES parameters must consist of key value pairs. A parameter block must be terminated by a blank line."
            end if

            call lower_case(words(1))

            ! insert here a readout from the pes file based on keywords in file input.nn for RuNNer when all the source code is implemented
            select case (words(1))

                case ('inp_dir')

                    read(words(2), '(A)') inp_path

                case ('prog_dir')

                    read(words(2), '(A)') prog_path


                case default
                    print *, "Error in the PES file: unknown nene parameter", words(1)
                    stop

            end select

        end do


        input_string = trim(inp_path) // "input.data"
        outforces_string = trim(inp_path) // "nnforces.out"
        outenergy_string = trim(inp_path) // "energy.out"
        prog_string = "cd " // trim(inp_path) // " && " // trim(prog_path) // " > temp"
        grep_string = "grep WARNING " // trim(inp_path) // "temp"


    end subroutine read_nene

    subroutine compute_nene(atoms, flag)

        ! Calculates energy and forces with HDNNPs

        type(universe), intent(inout)   :: atoms
        integer, intent(in)             :: flag

        character(len=max_string_length) :: buffer
        character(len=max_string_length) :: words(100)

        character(len=*), parameter :: err = "Error in compute_nene: "

        integer                         :: ios, eios, cios, j, k, nwords, index_counter
        real(dp)                        :: dummy_ce

        dummy_ce = 0.0_dp
        index_counter = 0

        !write input.data for RuNNer
        open(unit=21,file=input_string,status='replace',action='write',iostat=ios)

            if (ios == 0) then

                write (21,'(A5)')'begin'

                do k = 1,3

                    write(21,lattice_format) 'lattice', atoms%simbox(:,k) * ang2bohr

                end do

                do j = 1,atoms%natoms


                    write (21,atom_format) 'atom', atoms%r(:,:,j) * ang2bohr, atoms%name(atoms%idx(j)), dummy_ce, dummy_ce, atoms%f(:,:,j)

                end do

                write (21,ce_format) 'charge', dummy_ce
                write (21,ce_format) 'energy', dummy_ce
                write (21,'(A3)')'end'

            else

                write (*,*) 'Error writing input.data for RuNNer: Check if directory is correct! iostat = ', ios
                stop

            end if

        close(unit=21)

        !execute RuNNer
        call execute_command_line(prog_string, exitstat=eios, cmdstat=cios)
        call execute_command_line(grep_string)

            if (eios == 0 .and. cios == 0) then

                !read forces from nnforces.out calculated by RuNNer
                call open_for_read(22,outforces_string); ios = 0

                do while (ios == 0)
                    read(22, '(A)', iostat=ios) buffer
                    if (ios == 0) then
                        call split_string(buffer, words, nwords)

                        select case (words(1))

                             case ('Conf.')
                                     ! skip headline
                                     
                             case ('1') ! read first structure
                                index_counter = index_counter + 1


                                read(words(6),*,iostat=ios) atoms%f(1,:,index_counter)
                                if (ios /= 0) stop err // "Error when reading nnforces.out, force x value must be a number"
                                read(words(7),*,iostat=ios) atoms%f(2,:,index_counter)
                                if (ios /= 0) stop err // "Error when reading nnforces.out, force y value must be a number"
                                read(words(8),*,iostat=ios) atoms%f(3,:,index_counter)
                                if (ios /= 0) stop err // "Error when reading nnforces.out, force z value must be a number"

                             case default
                                print *, err // "Error when reading nnforces.out, unknown keyword"

                        end select

                    end if

                end do

                if (index_counter /= atoms%natoms) then
                        print *, err // "Error when reading nnforces.out, number of force values does not match with number of atoms"
                        stop
                end if

                close(unit=22)

                atoms%f(:,:,:) = atoms%f(:,:,:) * habohr2evang

                !read potential energy from energy.out calculated by RuNNer
                call open_for_read(23,outenergy_string); ios = 0

                do while (ios == 0)
                    read(23, '(A)', iostat=ios) buffer

                    if (ios == 0) then
                        call split_string(buffer, words, nwords)

                        select case (words(1))

                             case ('Conf.')
                                     ! skip headline

                             case ('1') ! read first structure

                                read(words(4),*,iostat=ios) atoms%epot
                                if (ios /= 0) stop err // "Error when reading energy.out, energy value must be a number"

                             case default
                                print *, err // "Error when reading energy.out, unknown keyword"
                                stop

                        end select

                    end if

                end do

                close(unit=23)

                atoms%epot = atoms%epot * ha2ev

            else

                write (*,*) 'Error executing RuNNer: Check if directory is correct! ', 'exitstat: ', eios, ' cmdstat: ', cios
                stop

            end if

    end subroutine compute_nene

end module pes_nene_mod
